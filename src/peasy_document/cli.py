"""Command-line interface for peasy-document conversions."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from peasy_document.engine import (
    csv_to_json,
    csv_to_markdown,
    html_to_markdown,
    html_to_text,
    json_to_csv,
    markdown_to_html,
)

app = typer.Typer(
    name="document",
    help="Document conversion — Markdown, HTML, CSV, JSON.",
    no_args_is_help=True,
)

InputArg = Annotated[Path, typer.Argument(help="Input file path.")]
OutputOpt = Annotated[
    Path | None,
    typer.Option("-o", "--output", help="Output file (default: stdout)."),
]
DelimiterOpt = Annotated[
    str,
    typer.Option("-d", "--delimiter", help="CSV delimiter character."),
]


def _write_output(content: str, output: Path | None) -> None:
    """Write *content* to *output* file or stdout."""
    if output is not None:
        output.write_text(content, encoding="utf-8")
        typer.echo(f"Written to {output}")
    else:
        typer.echo(content)


def _check_exists(path: Path) -> None:
    """Exit with error if *path* does not exist."""
    if not path.exists():
        typer.echo(f"Error: {path} not found.", err=True)
        raise typer.Exit(code=1)


@app.command("md-to-html")
def cmd_md_to_html(
    input_file: InputArg,
    output: OutputOpt = None,
) -> None:
    """Convert a Markdown file to HTML."""
    _check_exists(input_file)
    result = markdown_to_html(input_file)
    _write_output(result.content, output)


@app.command("html-to-text")
def cmd_html_to_text(
    input_file: InputArg,
    output: OutputOpt = None,
) -> None:
    """Strip HTML tags and extract plain text."""
    _check_exists(input_file)
    result = html_to_text(input_file)
    _write_output(result.content, output)


@app.command("csv-to-json")
def cmd_csv_to_json(
    input_file: InputArg,
    output: OutputOpt = None,
    delimiter: DelimiterOpt = ",",
) -> None:
    """Convert a CSV file to JSON."""
    _check_exists(input_file)
    result = csv_to_json(input_file, delimiter=delimiter)
    _write_output(result.content, output)


@app.command("json-to-csv")
def cmd_json_to_csv(
    input_file: InputArg,
    output: OutputOpt = None,
) -> None:
    """Convert a JSON array of objects to CSV."""
    _check_exists(input_file)
    result = json_to_csv(input_file)
    _write_output(result.content, output)


@app.command("csv-to-markdown")
def cmd_csv_to_markdown(
    input_file: InputArg,
    output: OutputOpt = None,
    delimiter: DelimiterOpt = ",",
) -> None:
    """Convert a CSV file to a Markdown table."""
    _check_exists(input_file)
    result = csv_to_markdown(input_file, delimiter=delimiter)
    _write_output(result.content, output)


@app.command("html-to-markdown")
def cmd_html_to_markdown(
    input_file: InputArg,
    output: OutputOpt = None,
) -> None:
    """Convert an HTML file to Markdown."""
    _check_exists(input_file)
    result = html_to_markdown(input_file)
    _write_output(result.content, output)


if __name__ == "__main__":
    app()
