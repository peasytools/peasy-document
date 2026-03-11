"""peasy-document — Document conversion library for Markdown, HTML, CSV, and JSON."""

from peasy_document.engine import (
    ConversionResult,
    TableData,
    TextInput,
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

__version__ = "0.1.0"

__all__ = [
    "ConversionResult",
    "TableData",
    "TextInput",
    "csv_to_html",
    "csv_to_json",
    "csv_to_markdown",
    "csv_to_table",
    "html_to_markdown",
    "html_to_text",
    "json_to_csv",
    "json_to_yaml",
    "markdown_to_html",
    "text_to_html",
]
