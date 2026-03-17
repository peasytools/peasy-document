# peasy-document

[![PyPI version](https://agentgif.com/badge/pypi/peasy-document/version.svg)](https://pypi.org/project/peasy-document/)
[![Python](https://img.shields.io/pypi/pyversions/peasy-document)](https://pypi.org/project/peasy-document/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Pure Python document conversion library with 10 conversion functions across 6 formats — Markdown, HTML, CSV, JSON, YAML, and plain text. Convert between document formats with frozen dataclass results, full conversion metadata, and only one lightweight dependency (`markdown`). Handles strings, bytes, and file paths uniformly through a single `TextInput` type, so you never have to worry about I/O boilerplate.

Built from the document conversion engine behind [PeasyDocument](https://peasytools.com), which provides interactive browser-based tools for Markdown to HTML conversion, CSV to JSON transformation, and HTML to Markdown extraction. The library covers 10 conversion paths with sub-millisecond performance for typical documents.

> **Try the interactive tools at [peasytools.com](https://peasytools.com)** — document conversion for Markdown, HTML, CSV, JSON, and YAML formats.

<p align="center">
  <img src="demo.gif" alt="peasy-document demo — Markdown to HTML, CSV to JSON conversion in Python REPL" width="800">
</p>

## Table of Contents

- [Install](#install)
- [Quick Start](#quick-start)
- [What You Can Do](#what-you-can-do)
  - [Markdown to HTML Conversion](#markdown-to-html-conversion)
  - [HTML Processing and Extraction](#html-processing-and-extraction)
  - [CSV and JSON Transformation](#csv-and-json-transformation)
  - [JSON to YAML Conversion](#json-to-yaml-conversion)
  - [Table Formatting and Rendering](#table-formatting-and-rendering)
- [Command-Line Interface](#command-line-interface)
- [API Reference](#api-reference)
  - [Conversion Functions](#conversion-functions)
  - [Types](#types)
- [Learn More About Document Conversion](#learn-more-about-document-conversion)
- [Also Available](#also-available)
- [Peasy Developer Tools](#peasy-developer-tools)
- [License](#license)

## Install

```bash
# Core library (only markdown dependency)
pip install peasy-document

# With CLI support
pip install "peasy-document[cli]"

# Everything
pip install "peasy-document[all]"
```

## Quick Start

```python
from peasy_document import markdown_to_html, csv_to_json, html_to_text

# Convert Markdown to HTML with tables, code highlighting, and TOC support
result = markdown_to_html("# Hello World\n\nThis is **bold** text.")
print(result.content)
# <h1>Hello World</h1>
# <p>This is <strong>bold</strong> text.</p>

# Convert CSV data to JSON array of objects
result = csv_to_json("name,age\nAlice,30\nBob,25")
print(result.content)
# [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]

# Strip HTML to plain text — removes all tags and decodes entities
result = html_to_text("<h1>Title</h1><p>Hello &amp; welcome.</p>")
print(result.content)
# Title
# Hello & welcome.
```

All functions return frozen dataclasses with conversion metadata — source format, target format, and byte sizes before and after conversion:

```python
# Every ConversionResult carries metadata about the transformation
result = markdown_to_html("# Hello")
print(result.source_format)  # "markdown"
print(result.target_format)  # "html"
print(result.source_size)    # 7 (bytes of input)
print(result.target_size)    # 18 (bytes of output)
```

## What You Can Do

### Markdown to HTML Conversion

Markdown is the de facto standard for developer documentation, README files, and technical writing. Defined by the [CommonMark specification](https://spec.commonmark.org/), Markdown provides a lightweight syntax that maps cleanly to HTML. peasy-document uses the battle-tested [Python-Markdown](https://python-markdown.github.io/) library under the hood, with sensible defaults that cover the most common use cases out of the box.

| Feature | Extension | Enabled by Default |
|---------|-----------|-------------------|
| Pipe tables | `tables` | Yes |
| Fenced code blocks | `fenced_code` | Yes |
| Syntax highlighting | `codehilite` | Yes |
| Table of contents | `toc` | Yes |
| Custom extensions | Pass any [Python-Markdown extension](https://python-markdown.github.io/extensions/) | Via `extensions=` kwarg |

```python
from peasy_document import markdown_to_html

# Convert Markdown with default extensions: tables, fenced_code, codehilite, toc
result = markdown_to_html("""
# API Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /users   | List users  |
| POST   | /users   | Create user |

```python
import requests
response = requests.get("/users")
\```
""")

# Override extensions for minimal output (tables + toc only)
result = markdown_to_html("content", extensions=["tables", "toc"])
```

Accepts `str`, `bytes`, or `Path` objects — read from files or process raw data without boilerplate:

```python
from pathlib import Path

# Read Markdown from a file and convert to HTML
result = markdown_to_html(Path("README.md"))

# Process binary content from an HTTP response or database blob
result = markdown_to_html(b"# Binary input works too")
```

Learn more: [Markdown to HTML Converter](https://peasyformats.com/doc/markdown-to-html/) · [Markdown vs Rich Text vs Plain Text](https://peasyformats.com/guides/markdown-vs-rich-text-vs-plain-text/) · [How to Convert Markdown to Other Formats](https://peasyformats.com/guides/how-to-convert-markdown-to-other-formats/)

### HTML Processing and Extraction

HTML is the backbone of the web, but extracting useful content from HTML documents often requires stripping tags, decoding entities (`&amp;` to `&`, `&lt;` to `<`), and ignoring non-content elements like `<script>` and `<style>` blocks. peasy-document provides two extraction paths: HTML to plain text for content indexing, and HTML to Markdown for content migration or CMS workflows.

Both functions use Python's stdlib `html.parser` — no external dependencies like BeautifulSoup or lxml required.

| Conversion | Use Case | Tags Handled |
|------------|----------|-------------|
| HTML to Text | Search indexing, content extraction, text analysis | Strips all tags, decodes entities, ignores `<script>`/`<style>` |
| HTML to Markdown | CMS migration, content republishing, documentation conversion | `p`, `h1`-`h6`, `a`, `strong`/`b`, `em`/`i`, `ul`/`ol`/`li`, `code`, `pre`, `br`, `img` |
| Text to HTML | Plain text formatting, email body generation | Wraps paragraphs in `<p>`, converts single newlines to `<br>` |

```python
from peasy_document import html_to_text, html_to_markdown, text_to_html

# Strip HTML to plain text — useful for search indexing and content analysis
result = html_to_text("""
<html>
<head><title>Page</title></head>
<body>
  <h1>Welcome</h1>
  <p>This is a <strong>formatted</strong> document with &amp; entities.</p>
  <script>alert('ignored')</script>
</body>
</html>
""")
print(result.content)
# Welcome
# This is a formatted document with & entities.

# Convert HTML to Markdown — preserves links, emphasis, headings, and lists
result = html_to_markdown("""
<h1>Document Title</h1>
<p>Visit <a href="https://example.com">our site</a> for <strong>more info</strong>.</p>
<ul>
  <li>First item</li>
  <li>Second item</li>
</ul>
""")
print(result.content)
# # Document Title
# Visit [our site](https://example.com) for **more info**.
# - First item
# - Second item

# Convert plain text to HTML paragraphs — double newlines become <p> tags
result = text_to_html("First paragraph.\n\nSecond paragraph.\nWith a line break.")
print(result.content)
# <p>First paragraph.</p>
# <p>Second paragraph.<br>With a line break.</p>
```

Learn more: [HTML Entities Encoder](https://peasyformats.com/doc/html-entities/) · [Plain Text vs Rich Text vs Markdown](https://peasyformats.com/guides/plain-text-vs-rich-text-vs-markdown/) · [What is MIME Sniffing?](https://peasyformats.com/glossary/mime-sniffing/)

### CSV and JSON Transformation

CSV (Comma-Separated Values) and JSON (JavaScript Object Notation) are the two most common data interchange formats. CSV, defined in [RFC 4180](https://datatracker.ietf.org/doc/html/rfc4180), represents tabular data with rows and columns. JSON, specified in [RFC 8259](https://datatracker.ietf.org/doc/html/rfc8259), represents structured data as nested objects and arrays. Converting between these two formats is one of the most frequent tasks in data processing pipelines, API integrations, and ETL workflows.

peasy-document handles both directions using Python's stdlib `csv` and `json` modules — no pandas or external data libraries required.

| Direction | Input Format | Output Format | Key Features |
|-----------|-------------|---------------|-------------|
| CSV to JSON | RFC 4180 CSV with header row | JSON array of objects | Custom delimiters, header-keyed objects |
| JSON to CSV | JSON array of objects | CSV with auto-detected headers | Handles inconsistent keys across objects |

```python
from peasy_document import csv_to_json, json_to_csv

# CSV to JSON — each row becomes a JSON object keyed by header values
result = csv_to_json("name,role,team\nAlice,Engineer,Backend\nBob,Designer,Frontend")
print(result.content)
# [
#   {"name": "Alice", "role": "Engineer", "team": "Backend"},
#   {"name": "Bob", "role": "Designer", "team": "Frontend"}
# ]

# Roundtrip: JSON back to CSV preserves column order
result = json_to_csv(result.content)
print(result.content)
# name,role,team
# Alice,Engineer,Backend
# Bob,Designer,Frontend

# Tab-separated values (TSV) — pass any single-character delimiter
result = csv_to_json("name\tage\nAlice\t30", delimiter="\t")

# Handles inconsistent keys gracefully — union of all keys becomes the header
result = json_to_csv('[{"a": 1, "b": 2}, {"b": 3, "c": 4}]')
# → a,b,c header with empty cells where keys are missing
```

Learn more: [CSV vs JSON vs XML Data Formats](https://peasyformats.com/guides/csv-vs-json-vs-xml/) · [What is TSV?](https://peasyformats.com/glossary/tsv/) · [CSV Format Reference](https://peasyformats.com/formats/csv/)

### JSON to YAML Conversion

YAML (YAML Ain't Markup Language) is widely used for configuration files — Kubernetes manifests, Docker Compose files, CI/CD pipelines, and infrastructure-as-code tools all rely on YAML's human-readable format. Converting JSON to YAML is a common need when moving between API responses (JSON) and configuration files (YAML).

peasy-document implements JSON-to-YAML conversion with a recursive pure-Python renderer. No PyYAML dependency is required. The converter handles nested objects, arrays, strings, numbers, booleans, and null values. Special characters in strings are automatically quoted per the [YAML 1.2 specification](https://yaml.org/spec/1.2/).

| YAML Feature | Supported | Notes |
|--------------|-----------|-------|
| Nested objects | Yes | Indented with 2 spaces |
| Arrays | Yes | Block sequence style (`- item`) |
| Strings with special chars | Yes | Auto-quoted (`":"`, `"#"`, brackets, etc.) |
| Reserved words | Yes | `true`, `false`, `null`, `yes`, `no` are quoted when used as strings |
| Numbers and booleans | Yes | Rendered without quotes |

```python
from peasy_document import json_to_yaml

# Convert a JSON config object to YAML — handles nested structures
result = json_to_yaml('{"server": {"host": "localhost", "port": 8080}, "debug": true}')
print(result.content)
# server:
#   host: localhost
#   port: 8080
# debug: true

# Arrays render as YAML block sequences
result = json_to_yaml('{"tags": ["python", "yaml", "json"], "count": 3}')
print(result.content)
# tags:
#   - python
#   - yaml
#   - json
# count: 3

# Special characters in values are auto-quoted for YAML safety
result = json_to_yaml('{"url": "https://example.com:8080/path#section"}')
print(result.content)
# url: "https://example.com:8080/path#section"
```

Learn more: [YAML JSON Converter](https://peasyformats.com/doc/yaml-json-converter/) · [JSON vs YAML vs TOML Configuration Formats](https://peasyformats.com/guides/json-vs-yaml-vs-toml/) · [YAML vs JSON vs TOML Configuration](https://peasyformats.com/guides/yaml-vs-json-vs-toml-configuration/)

### Table Formatting and Rendering

Tabular data can be rendered in multiple output formats depending on the target platform — Markdown tables for documentation, HTML tables for web pages, or structured `TableData` objects for programmatic access. peasy-document provides three rendering paths from CSV input, all using Python's stdlib `csv` module.

| Function | Output | Use Case |
|----------|--------|----------|
| `csv_to_table()` | `TableData` dataclass | Programmatic access to headers, rows, dimensions |
| `csv_to_markdown()` | Pipe-aligned Markdown table | GitHub README, documentation, Jupyter notebooks |
| `csv_to_html()` | `<table>` with `<thead>`/`<tbody>` | Web pages, email templates, reports |

```python
from peasy_document import csv_to_table, csv_to_markdown, csv_to_html

# Parse CSV into structured TableData — access headers, rows, and dimensions
table = csv_to_table("Name,Age,City\nAlice,30,NYC\nBob,25,LA")
print(table.headers)       # ['Name', 'Age', 'City']
print(table.row_count)     # 2
print(table.column_count)  # 3
print(table.rows[0])       # ['Alice', '30', 'NYC']

# Render as Markdown table with aligned columns
result = csv_to_markdown("Name,Age,City\nAlice,30,NYC\nBob,25,LA")
print(result.content)
# | Name  | Age | City |
# | ----- | --- | ---- |
# | Alice | 30  | NYC  |
# | Bob   | 25  | LA   |

# Render as HTML table with proper thead/tbody structure
result = csv_to_html("Name,Age\nAlice,30")
print(result.content)
# <table>
#   <thead>
#     <tr>
#       <th>Name</th>
#       <th>Age</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <td>Alice</td>
#       <td>30</td>
#     </tr>
#   </tbody>
# </table>
```

Learn more: [Document Format Interoperability Guide](https://peasyformats.com/guides/document-format-interoperability-guide/) · [What is Metadata Stripping?](https://peasyformats.com/glossary/metadata-stripping/) · [HTML Format Reference](https://peasyformats.com/formats/html/)

## Command-Line Interface

Install with CLI support: `pip install "peasy-document[cli]"`

The CLI exposes 6 conversion commands. All commands write to stdout by default — use `-o` / `--output` to write to a file.

```bash
# Convert Markdown to HTML
peasy-document md-to-html README.md -o output.html

# Strip HTML to plain text
peasy-document html-to-text page.html

# Convert CSV to JSON
peasy-document csv-to-json data.csv -o data.json

# Convert JSON array to CSV
peasy-document json-to-csv records.json -o records.csv

# CSV to Markdown table
peasy-document csv-to-markdown data.csv

# HTML to Markdown
peasy-document html-to-markdown page.html -o page.md
```

| Command | Description | Options |
|---------|-------------|---------|
| `md-to-html` | Convert Markdown file to HTML | `-o OUTPUT` |
| `html-to-text` | Strip HTML tags, extract plain text | `-o OUTPUT` |
| `csv-to-json` | Convert CSV to JSON array of objects | `-o OUTPUT`, `-d DELIMITER` |
| `json-to-csv` | Convert JSON array to CSV | `-o OUTPUT` |
| `csv-to-markdown` | Render CSV as Markdown table | `-o OUTPUT`, `-d DELIMITER` |
| `html-to-markdown` | Convert HTML to Markdown | `-o OUTPUT` |

## API Reference

### Conversion Functions

| Function | Input | Output | Dependencies |
|----------|-------|--------|-------------|
| `markdown_to_html(source, *, extensions=None)` | Markdown | HTML | `markdown` library |
| `html_to_text(source)` | HTML | Plain text | stdlib only |
| `html_to_markdown(source)` | HTML | Markdown | stdlib only |
| `text_to_html(source)` | Plain text | HTML | stdlib only |
| `csv_to_json(source, *, delimiter=",")` | CSV | JSON | stdlib only |
| `json_to_csv(source)` | JSON | CSV | stdlib only |
| `csv_to_table(source, *, delimiter=",")` | CSV | `TableData` | stdlib only |
| `csv_to_markdown(source, *, delimiter=",")` | CSV | Markdown table | stdlib only |
| `csv_to_html(source, *, delimiter=",")` | CSV | HTML table | stdlib only |
| `json_to_yaml(source)` | JSON | YAML | stdlib only |

All functions accept `TextInput` (`str | bytes | Path`) and return `ConversionResult` or `TableData`.

### Types

| Type | Description | Fields |
|------|-------------|--------|
| `TextInput` | Union type alias | `str \| bytes \| Path` |
| `ConversionResult` | Frozen dataclass — conversion output with metadata | `content: str`, `source_format: str`, `target_format: str`, `source_size: int`, `target_size: int` |
| `TableData` | Frozen dataclass — structured table representation | `headers: list[str]`, `rows: list[list[str]]`, `row_count: int`, `column_count: int` |

## Learn More About Document Conversion

- **Tools**: [Markdown to HTML](https://peasyformats.com/doc/markdown-to-html/) · [YAML JSON Converter](https://peasyformats.com/doc/yaml-json-converter/) · [Format Identifier](https://peasyformats.com/doc/format-identifier/) · [MIME Type Lookup](https://peasyformats.com/doc/mime-type-lookup/) · [Base64 Encoder](https://peasyformats.com/doc/base64-encoder/) · [URL Encoder](https://peasyformats.com/doc/url-encoder/) · [HTML Entities](https://peasyformats.com/doc/html-entities/) · [Line Ending Converter](https://peasyformats.com/doc/line-ending-converter/) · [Hex Dump Viewer](https://peasyformats.com/doc/hex-dump-viewer/) · [All Tools](https://peasyformats.com/)
- **Guides**: [JSON vs YAML vs TOML](https://peasyformats.com/guides/json-vs-yaml-vs-toml/) · [CSV vs JSON vs XML](https://peasyformats.com/guides/csv-vs-json-vs-xml/) · [Text Encoding UTF-8 ASCII](https://peasyformats.com/guides/text-encoding-utf8-ascii/) · [Markdown vs Rich Text vs Plain Text](https://peasyformats.com/guides/markdown-vs-rich-text-vs-plain-text/) · [How to Convert Markdown to Other Formats](https://peasyformats.com/guides/how-to-convert-markdown-to-other-formats/) · [Document Format Interoperability Guide](https://peasyformats.com/guides/document-format-interoperability-guide/) · [YAML vs JSON vs TOML Configuration](https://peasyformats.com/guides/yaml-vs-json-vs-toml-configuration/) · [All Guides](https://peasyformats.com/guides/)
- **Glossary**: [DOCX](https://peasyformats.com/glossary/docx/) · [EPUB](https://peasyformats.com/glossary/epub/) · [SVG](https://peasyformats.com/glossary/svg/) · [TSV](https://peasyformats.com/glossary/tsv/) · [ODF](https://peasyformats.com/glossary/odf/) · [MIME Sniffing](https://peasyformats.com/glossary/mime-sniffing/) · [File Signature](https://peasyformats.com/glossary/file-signature/) · [Metadata Stripping](https://peasyformats.com/glossary/metadata-stripping/) · [MessagePack](https://peasyformats.com/glossary/messagepack/) · [All Terms](https://peasyformats.com/glossary/)
- **Formats**: [CSV](https://peasyformats.com/formats/csv/) · [JSON](https://peasyformats.com/formats/json/) · [HTML](https://peasyformats.com/formats/html/) · [Markdown](https://peasyformats.com/formats/md/) · [YAML](https://peasyformats.com/formats/yaml/) · [XML](https://peasyformats.com/formats/xml/) · [TOML](https://peasyformats.com/formats/toml/) · [TXT](https://peasyformats.com/formats/txt/) · [TSV](https://peasyformats.com/formats/tsv/) · [RTF](https://peasyformats.com/formats/rtf/) · [DOCX](https://peasyformats.com/formats/docx/) · [All Formats](https://peasyformats.com/formats/)
- **API**: [REST API Docs](https://peasyformats.com/developers/) · [OpenAPI Spec](https://peasyformats.com/api/openapi.json)

## Also Available

| Platform | Install | Link |
|----------|---------|------|
| **TypeScript / npm** | `npm install peasy-document` | [npm](https://www.npmjs.com/package/peasy-document) |
| **Go** | `go get github.com/peasytools/peasy-document-go` | [pkg.go.dev](https://pkg.go.dev/github.com/peasytools/peasy-document-go) |
| **Rust** | `cargo add peasy-document` | [crates.io](https://crates.io/crates/peasy-document) |
| **Ruby** | `gem install peasy-document` | [RubyGems](https://rubygems.org/gems/peasy-document) |
| **MCP** | `uvx --from "peasy-document[mcp]" python -m peasy_document.mcp_server` | [Config](#mcp-server-claude-cursor-windsurf) |

## Peasy Developer Tools

Part of the [Peasy](https://peasytools.com) open-source developer tools ecosystem.

| Package | PyPI | npm | Description |
|---------|------|-----|-------------|
| peasy-pdf | [PyPI](https://pypi.org/project/peasy-pdf/) | [npm](https://www.npmjs.com/package/peasy-pdf) | PDF merge, split, compress, 21 operations — [peasypdf.com](https://peasypdf.com) |
| peasy-image | [PyPI](https://pypi.org/project/peasy-image/) | [npm](https://www.npmjs.com/package/peasy-image) | Image resize, crop, convert, compress, 20 operations — [peasyimage.com](https://peasyimage.com) |
| peasytext | [PyPI](https://pypi.org/project/peasytext/) | [npm](https://www.npmjs.com/package/peasytext) | Text case, slugify, word count, encoding — [peasytext.com](https://peasytext.com) |
| peasy-css | [PyPI](https://pypi.org/project/peasy-css/) | [npm](https://www.npmjs.com/package/peasy-css) | CSS gradients, shadows, flexbox, grid generators — [peasycss.com](https://peasycss.com) |
| peasy-compress | [PyPI](https://pypi.org/project/peasy-compress/) | [npm](https://www.npmjs.com/package/peasy-compress) | ZIP, TAR, gzip, brotli archive operations — [peasytools.com](https://peasytools.com) |
| **peasy-document** | **[PyPI](https://pypi.org/project/peasy-document/)** | **[npm](https://www.npmjs.com/package/peasy-document)** | **Markdown, HTML, CSV, JSON conversions — [peasyformats.com](https://peasyformats.com)** |
| peasy-audio | [PyPI](https://pypi.org/project/peasy-audio/) | [npm](https://www.npmjs.com/package/peasy-audio) | Audio convert, trim, merge, normalize — [peasyaudio.com](https://peasyaudio.com) |
| peasy-video | [PyPI](https://pypi.org/project/peasy-video/) | [npm](https://www.npmjs.com/package/peasy-video) | Video trim, resize, GIF conversion — [peasyvideo.com](https://peasyvideo.com) |

## License

MIT
