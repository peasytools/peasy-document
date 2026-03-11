# peasy-document

[![PyPI](https://img.shields.io/pypi/v/peasy-document)](https://pypi.org/project/peasy-document/)
[![Python](https://img.shields.io/pypi/pyversions/peasy-document)](https://pypi.org/project/peasy-document/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Pure Python document conversion library for Markdown, HTML, CSV, and JSON transformations. Convert between 6 document formats with 10 conversion functions, a CLI, and frozen dataclass results -- all with only one lightweight dependency (`markdown`). Built for developers who need fast, reliable document format conversions without heavyweight office-suite libraries.

Part of the [Peasy Tools](https://peasytools.com) developer tools ecosystem.

## Table of Contents

- [Install](#install)
- [Quick Start](#quick-start)
- [What You Can Do](#what-you-can-do)
  - [Markdown Conversion](#markdown-conversion)
  - [HTML Processing](#html-processing)
  - [CSV and JSON Conversion](#csv-and-json-conversion)
  - [Table Formatting](#table-formatting)
- [Command-Line Interface](#command-line-interface)
- [API Reference](#api-reference)
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

# Strip HTML to plain text
result = html_to_text("<h1>Title</h1><p>Hello &amp; welcome.</p>")
print(result.content)
# Title
# Hello & welcome.
```

All functions return frozen dataclasses with conversion metadata:

```python
result = markdown_to_html("# Hello")
print(result.source_format)  # "markdown"
print(result.target_format)  # "html"
print(result.source_size)    # 7 (bytes)
print(result.target_size)    # 18 (bytes)
```

## What You Can Do

### Markdown Conversion

Convert Markdown to HTML using the battle-tested `markdown` library with sensible defaults. Supports tables, fenced code blocks, syntax highlighting, and table of contents generation out of the box.

```python
from peasy_document import markdown_to_html

# Default extensions: tables, fenced_code, codehilite, toc
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

# Custom extensions
result = markdown_to_html("content", extensions=["tables", "toc"])
```

Accepts strings, bytes, or file paths:

```python
from pathlib import Path

# Read from file
result = markdown_to_html(Path("README.md"))

# Process raw bytes
result = markdown_to_html(b"# Binary input works too")
```

### HTML Processing

Extract plain text from HTML documents, stripping all tags and decoding HTML entities. Uses Python's stdlib `html.parser` -- no external dependencies needed.

```python
from peasy_document import html_to_text, html_to_markdown

# Strip HTML to plain text
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

# Convert HTML to Markdown (handles p, h1-h6, a, strong, em, lists, code, pre, img)
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
```

Convert plain text to HTML paragraphs:

```python
from peasy_document import text_to_html

# Wraps paragraphs in <p> tags, single newlines become <br>
result = text_to_html("First paragraph.\n\nSecond paragraph.\nWith a line break.")
print(result.content)
# <p>First paragraph.</p>
# <p>Second paragraph.<br>With a line break.</p>
```

### CSV and JSON Conversion

Transform between CSV and JSON formats using Python's stdlib `csv` and `json` modules. Supports custom delimiters, roundtrip conversion, and handles inconsistent keys gracefully.

```python
from peasy_document import csv_to_json, json_to_csv

# CSV to JSON array of objects
result = csv_to_json("name,role,team\nAlice,Engineer,Backend\nBob,Designer,Frontend")
print(result.content)
# [
#   {"name": "Alice", "role": "Engineer", "team": "Backend"},
#   {"name": "Bob", "role": "Designer", "team": "Frontend"}
# ]

# JSON back to CSV
result = json_to_csv(result.content)
print(result.content)
# name,role,team
# Alice,Engineer,Backend
# Bob,Designer,Frontend

# Tab-separated values
result = csv_to_json("name\tage\nAlice\t30", delimiter="\t")
```

Convert JSON to YAML-like format without any PyYAML dependency:

```python
from peasy_document import json_to_yaml

result = json_to_yaml('{"server": {"host": "localhost", "port": 8080}, "debug": true}')
print(result.content)
# server:
#   host: localhost
#   port: 8080
# debug: true
```

### Table Formatting

Parse CSV into structured table data, or render it directly as Markdown or HTML tables.

```python
from peasy_document import csv_to_table, csv_to_markdown, csv_to_html

# Parse into structured TableData
table = csv_to_table("Name,Age,City\nAlice,30,NYC\nBob,25,LA")
print(table.headers)       # ['Name', 'Age', 'City']
print(table.row_count)     # 2
print(table.column_count)  # 3
print(table.rows[0])       # ['Alice', '30', 'NYC']

# Render as Markdown table with proper alignment
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

## Command-Line Interface

Install with CLI support: `pip install "peasy-document[cli]"`

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

All commands write to stdout by default. Use `-o` / `--output` to write to a file.

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

All functions accept `TextInput` (str, bytes, or Path) and return `ConversionResult` or `TableData`.

### Types

| Type | Fields |
|------|--------|
| `ConversionResult` | `content`, `source_format`, `target_format`, `source_size`, `target_size` |
| `TableData` | `headers`, `rows`, `row_count`, `column_count` |

## Peasy Developer Tools

| Package | PyPI | Description |
|---------|------|-------------|
| **peasy-document** | [PyPI](https://pypi.org/project/peasy-document/) | Document conversion -- Markdown, HTML, CSV, JSON |
| peasy-pdf | [PyPI](https://pypi.org/project/peasy-pdf/) | PDF manipulation and conversion |
| peasy-image | [PyPI](https://pypi.org/project/peasy-image/) | Image format conversion and optimization |
| peasytext | [PyPI](https://pypi.org/project/peasytext/) | Text analysis and transformation |
| peasy-css | [PyPI](https://pypi.org/project/peasy-css/) | CSS minification and processing |
| peasy-compress | [PyPI](https://pypi.org/project/peasy-compress/) | File compression utilities |
| peasy-convert | [PyPI](https://pypi.org/project/peasy-convert/) | Unified CLI for all Peasy tools |

## License

MIT
