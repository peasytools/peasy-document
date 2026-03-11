"""Tests for peasy_document.engine — comprehensive coverage of all conversion functions."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from peasy_document.engine import (
    ConversionResult,
    TableData,
    csv_to_html,
    csv_to_json,
    csv_to_markdown,
    csv_to_table,
    html_to_markdown,
    html_to_text,
    json_to_csv,
    json_to_yaml,
    markdown_to_html,
    text_to_html,
)

# ---------------------------------------------------------------------------
# markdown_to_html
# ---------------------------------------------------------------------------


class TestMarkdownToHtml:
    def test_heading(self) -> None:
        result = markdown_to_html("# Hello World")
        assert "<h1" in result.content
        assert "Hello World" in result.content
        assert result.source_format == "markdown"
        assert result.target_format == "html"

    def test_paragraph(self) -> None:
        result = markdown_to_html("This is a paragraph.")
        assert "<p>" in result.content
        assert "This is a paragraph." in result.content

    def test_code_block(self) -> None:
        md = "```python\nprint('hello')\n```"
        result = markdown_to_html(md)
        assert "<code" in result.content
        assert "print" in result.content

    def test_table(self) -> None:
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = markdown_to_html(md)
        assert "<table>" in result.content or "<th>" in result.content

    def test_link(self) -> None:
        result = markdown_to_html("[Google](https://google.com)")
        assert 'href="https://google.com"' in result.content
        assert "Google" in result.content

    def test_custom_extensions(self) -> None:
        result = markdown_to_html("# Hello", extensions=[])
        assert "<h1>" in result.content

    def test_bytes_input(self) -> None:
        result = markdown_to_html(b"# Bytes Input")
        assert "<h1" in result.content
        assert "Bytes Input" in result.content

    def test_file_input(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# From File")
            f.flush()
            result = markdown_to_html(Path(f.name))
        assert "<h1" in result.content
        assert "From File" in result.content

    def test_source_and_target_sizes(self) -> None:
        source = "# Hello"
        result = markdown_to_html(source)
        assert result.source_size == len(source.encode("utf-8"))
        assert result.target_size == len(result.content.encode("utf-8"))

    def test_result_is_conversion_result(self) -> None:
        result = markdown_to_html("test")
        assert isinstance(result, ConversionResult)


# ---------------------------------------------------------------------------
# html_to_text
# ---------------------------------------------------------------------------


class TestHtmlToText:
    def test_strip_tags(self) -> None:
        result = html_to_text("<p>Hello <strong>World</strong></p>")
        assert "Hello World" in result.content
        assert "<p>" not in result.content
        assert "<strong>" not in result.content

    def test_decode_entities(self) -> None:
        result = html_to_text("<p>A &amp; B &lt; C</p>")
        assert "A & B < C" in result.content

    def test_whitespace_handling(self) -> None:
        result = html_to_text("<p>  Too   many   spaces  </p>")
        assert "Too many spaces" in result.content

    def test_script_and_style_stripped(self) -> None:
        html = "<p>visible</p><script>alert('x')</script><style>.x{}</style><p>also visible</p>"
        result = html_to_text(html)
        assert "visible" in result.content
        assert "also visible" in result.content
        assert "alert" not in result.content
        assert ".x{}" not in result.content

    def test_block_elements_add_newlines(self) -> None:
        result = html_to_text("<h1>Title</h1><p>Body</p>")
        assert "Title" in result.content
        assert "Body" in result.content

    def test_numeric_entity(self) -> None:
        result = html_to_text("<p>&#169; 2026</p>")
        assert "\u00a9 2026" in result.content


# ---------------------------------------------------------------------------
# csv_to_json
# ---------------------------------------------------------------------------


class TestCsvToJson:
    def test_basic_conversion(self) -> None:
        csv_data = "name,age\nAlice,30\nBob,25"
        result = csv_to_json(csv_data)
        data = json.loads(result.content)
        assert len(data) == 2
        assert data[0]["name"] == "Alice"
        assert data[0]["age"] == "30"
        assert result.source_format == "csv"
        assert result.target_format == "json"

    def test_custom_delimiter(self) -> None:
        csv_data = "name;age\nAlice;30"
        result = csv_to_json(csv_data, delimiter=";")
        data = json.loads(result.content)
        assert data[0]["name"] == "Alice"

    def test_empty_csv(self) -> None:
        result = csv_to_json("")
        data = json.loads(result.content)
        assert data == []

    def test_single_row(self) -> None:
        csv_data = "a,b,c\n1,2,3"
        result = csv_to_json(csv_data)
        data = json.loads(result.content)
        assert len(data) == 1
        assert data[0] == {"a": "1", "b": "2", "c": "3"}


# ---------------------------------------------------------------------------
# json_to_csv
# ---------------------------------------------------------------------------


class TestJsonToCsv:
    def test_basic_conversion(self) -> None:
        data = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
        result = json_to_csv(json.dumps(data))
        assert "name" in result.content
        assert "Alice" in result.content
        assert result.source_format == "json"
        assert result.target_format == "csv"

    def test_empty_array(self) -> None:
        result = json_to_csv("[]")
        assert result.content == ""
        assert result.target_size == 0

    def test_roundtrip_csv_json_csv(self) -> None:
        original = "name,age\nAlice,30\nBob,25"
        json_result = csv_to_json(original)
        csv_result = json_to_csv(json_result.content)
        assert "Alice" in csv_result.content
        assert "Bob" in csv_result.content

    def test_inconsistent_keys(self) -> None:
        data = [{"a": "1", "b": "2"}, {"b": "3", "c": "4"}]
        result = json_to_csv(json.dumps(data))
        assert "a" in result.content
        assert "b" in result.content
        assert "c" in result.content


# ---------------------------------------------------------------------------
# csv_to_table
# ---------------------------------------------------------------------------


class TestCsvToTable:
    def test_basic(self) -> None:
        csv_data = "name,age\nAlice,30\nBob,25"
        table = csv_to_table(csv_data)
        assert isinstance(table, TableData)
        assert table.headers == ["name", "age"]
        assert table.row_count == 2
        assert table.column_count == 2
        assert table.rows[0] == ["Alice", "30"]

    def test_empty(self) -> None:
        table = csv_to_table("")
        assert table.headers == []
        assert table.rows == []
        assert table.row_count == 0
        assert table.column_count == 0

    def test_headers_only(self) -> None:
        table = csv_to_table("a,b,c")
        assert table.headers == ["a", "b", "c"]
        assert table.row_count == 0
        assert table.column_count == 3

    def test_tab_delimiter(self) -> None:
        csv_data = "x\ty\n1\t2"
        table = csv_to_table(csv_data, delimiter="\t")
        assert table.headers == ["x", "y"]
        assert table.rows[0] == ["1", "2"]


# ---------------------------------------------------------------------------
# csv_to_markdown
# ---------------------------------------------------------------------------


class TestCsvToMarkdown:
    def test_basic(self) -> None:
        csv_data = "Name,Age\nAlice,30\nBob,25"
        result = csv_to_markdown(csv_data)
        assert "| Name" in result.content
        assert "| ---" in result.content or "|---" in result.content
        assert "| Alice" in result.content
        assert result.source_format == "csv"
        assert result.target_format == "markdown"

    def test_empty(self) -> None:
        result = csv_to_markdown("")
        assert result.content == ""

    def test_alignment(self) -> None:
        csv_data = "A,BB\n1,22"
        result = csv_to_markdown(csv_data)
        lines = result.content.strip().split("\n")
        assert len(lines) == 3  # header + separator + 1 data row
        # Separator line should have dashes
        assert "-" in lines[1]


# ---------------------------------------------------------------------------
# csv_to_html
# ---------------------------------------------------------------------------


class TestCsvToHtml:
    def test_basic(self) -> None:
        csv_data = "Name,Age\nAlice,30"
        result = csv_to_html(csv_data)
        assert "<table>" in result.content
        assert "<th>Name</th>" in result.content
        assert "<td>Alice</td>" in result.content
        assert "<td>30</td>" in result.content
        assert "</table>" in result.content

    def test_empty(self) -> None:
        result = csv_to_html("")
        assert "<table></table>" in result.content

    def test_html_escaping(self) -> None:
        csv_data = "text\n<script>alert('xss')</script>"
        result = csv_to_html(csv_data)
        assert "<script>" not in result.content
        assert "&lt;script&gt;" in result.content


# ---------------------------------------------------------------------------
# json_to_yaml
# ---------------------------------------------------------------------------


class TestJsonToYaml:
    def test_simple_object(self) -> None:
        data = {"name": "Alice", "age": 30}
        result = json_to_yaml(json.dumps(data))
        assert "name: Alice" in result.content
        assert "age: 30" in result.content
        assert result.source_format == "json"
        assert result.target_format == "yaml"

    def test_nested_object(self) -> None:
        data = {"person": {"name": "Alice", "age": 30}}
        result = json_to_yaml(json.dumps(data))
        assert "person:" in result.content
        assert "name: Alice" in result.content

    def test_array(self) -> None:
        data = {"items": ["a", "b", "c"]}
        result = json_to_yaml(json.dumps(data))
        assert "items:" in result.content
        assert "- a" in result.content
        assert "- b" in result.content

    def test_boolean_and_null(self) -> None:
        data = {"active": True, "deleted": False, "value": None}
        result = json_to_yaml(json.dumps(data))
        assert "active: true" in result.content
        assert "deleted: false" in result.content
        assert "value: null" in result.content

    def test_special_characters_quoted(self) -> None:
        data = {"msg": "hello: world"}
        result = json_to_yaml(json.dumps(data))
        assert '"hello: world"' in result.content

    def test_top_level_array(self) -> None:
        data = [1, 2, 3]
        result = json_to_yaml(json.dumps(data))
        assert "- 1" in result.content
        assert "- 2" in result.content


# ---------------------------------------------------------------------------
# text_to_html
# ---------------------------------------------------------------------------


class TestTextToHtml:
    def test_single_paragraph(self) -> None:
        result = text_to_html("Hello world.")
        assert "<p>Hello world.</p>" in result.content

    def test_multiple_paragraphs(self) -> None:
        result = text_to_html("First paragraph.\n\nSecond paragraph.")
        assert "<p>First paragraph.</p>" in result.content
        assert "<p>Second paragraph.</p>" in result.content

    def test_empty_input(self) -> None:
        result = text_to_html("")
        assert result.content == ""
        assert result.target_size == 0

    def test_whitespace_only(self) -> None:
        result = text_to_html("   \n\n   ")
        assert result.content == ""

    def test_html_escaping(self) -> None:
        result = text_to_html("<script>alert('x')</script>")
        assert "<script>" not in result.content
        assert "&lt;script&gt;" in result.content

    def test_single_newlines_become_br(self) -> None:
        result = text_to_html("Line one\nLine two")
        assert "<br>" in result.content


# ---------------------------------------------------------------------------
# html_to_markdown
# ---------------------------------------------------------------------------


class TestHtmlToMarkdown:
    def test_headings(self) -> None:
        result = html_to_markdown("<h1>Title</h1>")
        assert "# Title" in result.content

    def test_h2(self) -> None:
        result = html_to_markdown("<h2>Subtitle</h2>")
        assert "## Subtitle" in result.content

    def test_paragraph(self) -> None:
        result = html_to_markdown("<p>Hello world.</p>")
        assert "Hello world." in result.content

    def test_bold_and_italic(self) -> None:
        result = html_to_markdown("<p><strong>bold</strong> and <em>italic</em></p>")
        assert "**bold**" in result.content
        assert "*italic*" in result.content

    def test_link(self) -> None:
        result = html_to_markdown('<a href="https://example.com">Example</a>')
        assert "[Example](https://example.com)" in result.content

    def test_image(self) -> None:
        result = html_to_markdown('<img src="photo.jpg" alt="A photo">')
        assert "![A photo](photo.jpg)" in result.content

    def test_unordered_list(self) -> None:
        html = "<ul><li>First</li><li>Second</li></ul>"
        result = html_to_markdown(html)
        assert "- First" in result.content
        assert "- Second" in result.content

    def test_ordered_list(self) -> None:
        html = "<ol><li>First</li><li>Second</li></ol>"
        result = html_to_markdown(html)
        assert "1. First" in result.content
        assert "2. Second" in result.content

    def test_inline_code(self) -> None:
        result = html_to_markdown("<p>Use <code>pip install</code> to install.</p>")
        assert "`pip install`" in result.content

    def test_code_block(self) -> None:
        result = html_to_markdown("<pre><code>print('hello')</code></pre>")
        assert "```" in result.content
        assert "print('hello')" in result.content

    def test_br_tag(self) -> None:
        result = html_to_markdown("<p>Line one<br>Line two</p>")
        assert "  \n" in result.content

    def test_entity_decoding(self) -> None:
        result = html_to_markdown("<p>A &amp; B</p>")
        assert "A & B" in result.content

    def test_complex_document(self) -> None:
        html = """
        <h1>Document</h1>
        <p>This is a <strong>complex</strong> document with <a href="http://x.com">links</a>.</p>
        <h2>Section</h2>
        <ul><li>Item 1</li><li>Item 2</li></ul>
        """
        result = html_to_markdown(html)
        assert "# Document" in result.content
        assert "**complex**" in result.content
        assert "[links](http://x.com)" in result.content
        assert "## Section" in result.content
        assert "- Item 1" in result.content


# ---------------------------------------------------------------------------
# Cross-cutting / edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_conversion_result_frozen(self) -> None:
        result = markdown_to_html("# Test")
        with pytest.raises(AttributeError):
            result.content = "modified"  # type: ignore[misc]

    def test_table_data_frozen(self) -> None:
        table = csv_to_table("a,b\n1,2")
        with pytest.raises(AttributeError):
            table.headers = []  # type: ignore[misc]

    def test_unicode_content(self) -> None:
        result = markdown_to_html("# \u3053\u3093\u306b\u3061\u306f")
        assert "\u3053\u3093\u306b\u3061\u306f" in result.content

    def test_large_csv(self) -> None:
        rows = ["col1,col2"] + [f"val{i},data{i}" for i in range(100)]
        csv_data = "\n".join(rows)
        result = csv_to_json(csv_data)
        data = json.loads(result.content)
        assert len(data) == 100
