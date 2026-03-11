"""Document conversion engine — pure functions for Markdown, HTML, CSV, JSON transformations.

All functions accept ``TextInput`` (str, bytes, or Path) and return frozen dataclasses.
Only stdlib + the ``markdown`` library are used — no heavyweight dependencies.
"""

from __future__ import annotations

import csv
import html
import io
import json
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

TextInput = str | bytes | Path


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConversionResult:
    """Immutable result of a document conversion."""

    content: str
    source_format: str
    target_format: str
    source_size: int
    target_size: int


@dataclass(frozen=True)
class TableData:
    """Structured table data parsed from CSV or similar tabular source."""

    headers: list[str]
    rows: list[list[str]]
    row_count: int
    column_count: int


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _read_text(source: TextInput) -> str:
    """Normalize *source* to a string."""
    if isinstance(source, Path):
        return source.read_text(encoding="utf-8")
    if isinstance(source, bytes):
        return source.decode("utf-8")
    return source


def _source_size(source: TextInput) -> int:
    """Return the byte-length of *source* before conversion."""
    if isinstance(source, Path):
        return source.stat().st_size
    if isinstance(source, bytes):
        return len(source)
    return len(source.encode("utf-8"))


# ---------------------------------------------------------------------------
# HTML → plain-text parser
# ---------------------------------------------------------------------------


class _HTMLToTextParser(HTMLParser):
    """Strip HTML tags and decode entities, producing plain text."""

    _BLOCK_TAGS = frozenset(
        {
            "p",
            "div",
            "br",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "li",
            "tr",
            "blockquote",
            "pre",
            "hr",
        }
    )

    def __init__(self) -> None:
        super().__init__()
        self._pieces: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self._skip = True
        if tag in self._BLOCK_TAGS:
            self._pieces.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._skip = False
        if tag in self._BLOCK_TAGS:
            self._pieces.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self._pieces.append(data)

    def handle_entityref(self, name: str) -> None:
        char = html.unescape(f"&{name};")
        self._pieces.append(char)

    def handle_charref(self, name: str) -> None:
        char = html.unescape(f"&#{name};")
        self._pieces.append(char)

    def get_text(self) -> str:
        raw = "".join(self._pieces)
        # Collapse runs of whitespace within lines, then collapse blank lines
        lines = [" ".join(line.split()) for line in raw.splitlines()]
        text = "\n".join(lines)
        # Collapse multiple blank lines into at most two newlines
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        return text.strip()


# ---------------------------------------------------------------------------
# HTML → Markdown parser
# ---------------------------------------------------------------------------


class _HTMLToMarkdownParser(HTMLParser):
    """Convert basic HTML to Markdown using stdlib html.parser."""

    def __init__(self) -> None:
        super().__init__()
        self._pieces: list[str] = []
        self._tag_stack: list[str] = []
        self._list_stack: list[str] = []  # "ul" or "ol"
        self._ol_counters: list[int] = []
        self._href: str | None = None
        self._link_text_pieces: list[str] = []
        self._in_link = False
        self._in_pre = False
        self._in_code = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        self._tag_stack.append(tag)

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self._pieces.append("\n" + "#" * level + " ")
        elif tag == "p":
            self._pieces.append("\n\n")
        elif tag == "br":
            self._pieces.append("  \n")
        elif tag == "strong" or tag == "b":
            self._pieces.append("**")
        elif tag == "em" or tag == "i":
            self._pieces.append("*")
        elif tag == "a":
            self._in_link = True
            self._href = attrs_dict.get("href", "")
            self._link_text_pieces = []
        elif tag == "img":
            alt = attrs_dict.get("alt", "")
            src = attrs_dict.get("src", "")
            self._pieces.append(f"![{alt}]({src})")
        elif tag == "ul":
            self._list_stack.append("ul")
            self._pieces.append("\n")
        elif tag == "ol":
            self._list_stack.append("ol")
            self._ol_counters.append(0)
            self._pieces.append("\n")
        elif tag == "li":
            indent = "  " * max(0, len(self._list_stack) - 1)
            if self._list_stack and self._list_stack[-1] == "ol":
                self._ol_counters[-1] += 1
                self._pieces.append(f"{indent}{self._ol_counters[-1]}. ")
            else:
                self._pieces.append(f"{indent}- ")
        elif tag == "pre":
            self._in_pre = True
            self._pieces.append("\n\n```\n")
        elif tag == "code":
            if not self._in_pre:
                self._in_code = True
                self._pieces.append("`")

    def handle_endtag(self, tag: str) -> None:
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._pieces.append("\n")
        elif tag == "p":
            self._pieces.append("\n")
        elif tag == "strong" or tag == "b":
            self._pieces.append("**")
        elif tag == "em" or tag == "i":
            self._pieces.append("*")
        elif tag == "a":
            link_text = "".join(self._link_text_pieces)
            self._pieces.append(f"[{link_text}]({self._href})")
            self._in_link = False
            self._href = None
            self._link_text_pieces = []
        elif tag == "ul":
            if self._list_stack:
                self._list_stack.pop()
            self._pieces.append("\n")
        elif tag == "ol":
            if self._list_stack:
                self._list_stack.pop()
            if self._ol_counters:
                self._ol_counters.pop()
            self._pieces.append("\n")
        elif tag == "li":
            self._pieces.append("\n")
        elif tag == "pre":
            self._in_pre = False
            self._pieces.append("```\n\n")
        elif tag == "code":
            if not self._in_pre:
                self._in_code = False
                self._pieces.append("`")

    def handle_data(self, data: str) -> None:
        if self._in_link:
            self._link_text_pieces.append(data)
        else:
            self._pieces.append(data)

    def handle_entityref(self, name: str) -> None:
        char = html.unescape(f"&{name};")
        if self._in_link:
            self._link_text_pieces.append(char)
        else:
            self._pieces.append(char)

    def handle_charref(self, name: str) -> None:
        char = html.unescape(f"&#{name};")
        if self._in_link:
            self._link_text_pieces.append(char)
        else:
            self._pieces.append(char)

    def get_markdown(self) -> str:
        raw = "".join(self._pieces)
        # Clean up excessive blank lines
        while "\n\n\n" in raw:
            raw = raw.replace("\n\n\n", "\n\n")
        return raw.strip()


# ---------------------------------------------------------------------------
# JSON → YAML helper (no PyYAML dependency)
# ---------------------------------------------------------------------------


def _to_yaml_lines(obj: object, indent: int = 0) -> list[str]:
    """Recursively convert a Python object to YAML-like lines."""
    prefix = "  " * indent
    lines: list[str] = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.extend(_to_yaml_lines(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict | list):
                        lines.append(f"{prefix}  -")
                        sub_lines = _to_yaml_lines(item, indent + 2)
                        lines.extend(sub_lines)
                    else:
                        lines.append(f"{prefix}  - {_yaml_scalar(item)}")
            else:
                lines.append(f"{prefix}{key}: {_yaml_scalar(value)}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict | list):
                lines.append(f"{prefix}-")
                sub_lines = _to_yaml_lines(item, indent + 1)
                lines.extend(sub_lines)
            else:
                lines.append(f"{prefix}- {_yaml_scalar(item)}")
    else:
        lines.append(f"{prefix}{_yaml_scalar(obj)}")

    return lines


def _yaml_scalar(value: object) -> str:
    """Format a scalar value for YAML output."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    # String — quote if it contains special characters
    s = str(value)
    if any(c in s for c in (":", "#", "[", "]", "{", "}", ",", "&", "*", "!", "|", ">", "'", '"')):
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if s in ("true", "false", "null", "yes", "no", "on", "off"):
        return f'"{s}"'
    if not s:
        return '""'
    return s


# ---------------------------------------------------------------------------
# Public conversion functions
# ---------------------------------------------------------------------------


def markdown_to_html(
    source: TextInput,
    *,
    extensions: list[str] | None = None,
) -> ConversionResult:
    """Convert Markdown to HTML.

    Uses the ``markdown`` library with sensible default extensions:
    tables, fenced_code, codehilite, and toc.
    """
    import markdown as md_lib

    if extensions is None:
        extensions = ["tables", "fenced_code", "codehilite", "toc"]

    src_size = _source_size(source)
    text = _read_text(source)
    result = md_lib.markdown(text, extensions=extensions)

    return ConversionResult(
        content=result,
        source_format="markdown",
        target_format="html",
        source_size=src_size,
        target_size=len(result.encode("utf-8")),
    )


def html_to_text(source: TextInput) -> ConversionResult:
    """Strip HTML tags and decode entities, producing plain text.

    Uses stdlib ``html.parser`` — no external dependencies.
    """
    src_size = _source_size(source)
    text = _read_text(source)

    parser = _HTMLToTextParser()
    parser.feed(text)
    result = parser.get_text()

    return ConversionResult(
        content=result,
        source_format="html",
        target_format="text",
        source_size=src_size,
        target_size=len(result.encode("utf-8")),
    )


def csv_to_json(
    source: TextInput,
    *,
    delimiter: str = ",",
) -> ConversionResult:
    """Parse CSV to a JSON array of objects.

    Each row becomes a JSON object keyed by the header row values.
    """
    src_size = _source_size(source)
    text = _read_text(source)

    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    result = json.dumps(rows, ensure_ascii=False, indent=2)

    return ConversionResult(
        content=result,
        source_format="csv",
        target_format="json",
        source_size=src_size,
        target_size=len(result.encode("utf-8")),
    )


def json_to_csv(source: TextInput) -> ConversionResult:
    """Convert a JSON array of objects to CSV string.

    Keys from the first object are used as CSV headers. All objects are
    expected to share the same keys.
    """
    src_size = _source_size(source)
    text = _read_text(source)

    data = json.loads(text)
    if not isinstance(data, list) or not data:
        result = ""
        return ConversionResult(
            content=result,
            source_format="json",
            target_format="csv",
            source_size=src_size,
            target_size=0,
        )

    # Collect all keys across all objects to handle inconsistent rows
    all_keys: list[str] = []
    seen: set[str] = set()
    for item in data:
        if isinstance(item, dict):
            for key in item:
                if key not in seen:
                    all_keys.append(key)
                    seen.add(key)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=all_keys, extrasaction="ignore")
    writer.writeheader()
    for item in data:
        if isinstance(item, dict):
            writer.writerow(item)

    result = output.getvalue()
    return ConversionResult(
        content=result,
        source_format="json",
        target_format="csv",
        source_size=src_size,
        target_size=len(result.encode("utf-8")),
    )


def csv_to_table(
    source: TextInput,
    *,
    delimiter: str = ",",
) -> TableData:
    """Parse CSV into structured :class:`TableData`."""
    text = _read_text(source)
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    all_rows = list(reader)

    if not all_rows:
        return TableData(headers=[], rows=[], row_count=0, column_count=0)

    headers = all_rows[0]
    rows = all_rows[1:]
    return TableData(
        headers=headers,
        rows=rows,
        row_count=len(rows),
        column_count=len(headers),
    )


def csv_to_markdown(
    source: TextInput,
    *,
    delimiter: str = ",",
) -> ConversionResult:
    """Convert CSV to a Markdown table with pipes and a separator row."""
    src_size = _source_size(source)
    table = csv_to_table(source, delimiter=delimiter)

    if not table.headers:
        return ConversionResult(
            content="",
            source_format="csv",
            target_format="markdown",
            source_size=src_size,
            target_size=0,
        )

    # Calculate column widths for alignment
    widths = [len(h) for h in table.headers]
    for row in table.rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))

    # Build header
    header_cells = [h.ljust(widths[i]) for i, h in enumerate(table.headers)]
    header_line = "| " + " | ".join(header_cells) + " |"

    # Build separator
    sep_cells = ["-" * widths[i] for i in range(len(table.headers))]
    sep_line = "| " + " | ".join(sep_cells) + " |"

    # Build data rows
    data_lines: list[str] = []
    for row in table.rows:
        cells: list[str] = []
        for i, _h in enumerate(table.headers):
            value = row[i] if i < len(row) else ""
            cells.append(value.ljust(widths[i]))
        data_lines.append("| " + " | ".join(cells) + " |")

    result = "\n".join([header_line, sep_line, *data_lines])
    return ConversionResult(
        content=result,
        source_format="csv",
        target_format="markdown",
        source_size=src_size,
        target_size=len(result.encode("utf-8")),
    )


def csv_to_html(
    source: TextInput,
    *,
    delimiter: str = ",",
) -> ConversionResult:
    """Convert CSV to an HTML ``<table>`` element."""
    src_size = _source_size(source)
    table = csv_to_table(source, delimiter=delimiter)

    if not table.headers:
        return ConversionResult(
            content="<table></table>",
            source_format="csv",
            target_format="html",
            source_size=src_size,
            target_size=len(b"<table></table>"),
        )

    lines: list[str] = ["<table>", "  <thead>", "    <tr>"]
    for h in table.headers:
        escaped = html.escape(h)
        lines.append(f"      <th>{escaped}</th>")
    lines.extend(["    </tr>", "  </thead>", "  <tbody>"])

    for row in table.rows:
        lines.append("    <tr>")
        for i in range(len(table.headers)):
            value = row[i] if i < len(row) else ""
            escaped = html.escape(value)
            lines.append(f"      <td>{escaped}</td>")
        lines.append("    </tr>")

    lines.extend(["  </tbody>", "</table>"])
    result = "\n".join(lines)

    return ConversionResult(
        content=result,
        source_format="csv",
        target_format="html",
        source_size=src_size,
        target_size=len(result.encode("utf-8")),
    )


def json_to_yaml(source: TextInput) -> ConversionResult:
    """Convert JSON to YAML-like format.

    Uses a simple recursive implementation — no PyYAML dependency required.
    Handles nested objects, arrays, strings, numbers, booleans, and null.
    """
    src_size = _source_size(source)
    text = _read_text(source)

    data = json.loads(text)
    lines = _to_yaml_lines(data)
    result = "\n".join(lines)

    return ConversionResult(
        content=result,
        source_format="json",
        target_format="yaml",
        source_size=src_size,
        target_size=len(result.encode("utf-8")),
    )


def text_to_html(source: TextInput) -> ConversionResult:
    """Wrap plain text in HTML paragraphs.

    Splits on double newlines to form ``<p>`` elements. Single newlines
    within a paragraph become ``<br>`` tags.
    """
    src_size = _source_size(source)
    text = _read_text(source)

    if not text.strip():
        return ConversionResult(
            content="",
            source_format="text",
            target_format="html",
            source_size=src_size,
            target_size=0,
        )

    # Split on double newlines to find paragraphs
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    html_parts: list[str] = []
    for para in paragraphs:
        escaped = html.escape(para)
        # Convert single newlines to <br>
        escaped = escaped.replace("\n", "<br>")
        html_parts.append(f"<p>{escaped}</p>")

    result = "\n".join(html_parts)
    return ConversionResult(
        content=result,
        source_format="text",
        target_format="html",
        source_size=src_size,
        target_size=len(result.encode("utf-8")),
    )


def html_to_markdown(source: TextInput) -> ConversionResult:
    """Convert basic HTML to Markdown.

    Handles ``p``, ``h1``-``h6``, ``a``, ``strong``/``b``, ``em``/``i``,
    ``ul``/``ol``/``li``, ``code``, ``pre``, ``br``, and ``img`` tags
    using stdlib ``html.parser``.
    """
    src_size = _source_size(source)
    text = _read_text(source)

    parser = _HTMLToMarkdownParser()
    parser.feed(text)
    result = parser.get_markdown()

    return ConversionResult(
        content=result,
        source_format="html",
        target_format="markdown",
        source_size=src_size,
        target_size=len(result.encode("utf-8")),
    )
