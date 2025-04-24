from pathlib import Path
from typing import Literal, cast  # Añadimos cast para el tipado

import click
from rich.console import Console
from rich.table import Table

from .config import URL_MODES  # Importamos URL_MODES para el tipado
from .config import (
    DEFAULT_EXCLUDE_DIRS,
    DEFAULT_INCLUDE_EXTENSIONS,
    MARKITDOWN_EXTENSIONS,
)
from .core import ReadConfig, Readium, is_url
from .utils.error_handling import print_error

console = Console()


@click.command(
    help="""
Read and analyze documentation from directories, repositories, or URLs.

Examples:
    # Process a local directory
    readium /path/to/directory

    # Process a Git repository
    readium https://github.com/username/repository

    # Process a webpage and convert to Markdown
    readium https://example.com/docs

    # Process a webpage with custom output
    readium https://example.com/docs -o docs.md

    # Save output to a file
    readium /path/to/directory -o output.md

    # Generate split files from a webpage
    readium https://example.com/docs --split-output ./markdown-files/

    # Exclude specific file extensions
    readium /path/to/directory --exclude-ext .json --exclude-ext .yml

    # Exclude multiple directories (using -x multiple times)
    readium /path/to/directory -x dir1 -x dir2

Note: Do not use empty values with -x/--exclude-dir. Each value must be a valid directory name.
"""
)
@click.argument("path", type=str)
@click.option(
    "--target-dir", "-t", help="Target subdirectory to analyze (for directories)"
)
@click.option(
    "--branch", "-b", help="Specific Git branch to clone (only for Git repositories)"
)
@click.option(
    "--max-size",
    "-s",
    type=int,
    default=5 * 1024 * 1024,
    help="Maximum file size in bytes (default: 5MB)",
)
@click.option(
    "--output", "-o", type=click.Path(), help="Output file path for combined results"
)
@click.option(
    "--split-output",
    type=click.Path(),
    help="Directory path for split output files (each file gets its own UUID-named file)",
)
@click.option(
    "--exclude-dir",
    "-x",
    multiple=True,
    help="Additional directories to exclude (for directories)",
)
@click.option(
    "--include-ext",
    "-i",
    multiple=True,
    help="Additional extensions to include (for directories)",
)
@click.option(
    "--url-mode",
    type=click.Choice(["full", "clean"]),
    default="clean",
    help="URL processing mode: 'full' preserves all content, 'clean' extracts main content only (default: clean)",
)
@click.option(
    "--exclude-ext",
    "-e",
    multiple=True,
    help="File extensions to exclude from processing (can be specified multiple times, e.g. --exclude-ext .json --exclude-ext .yml)",
)
@click.option(
    "--debug/--no-debug",
    "-d/-D",
    default=False,
    help="Enable debug mode",
)
@click.option(
    "--use-markitdown/--no-markitdown",
    default=False,
    help="Use MarkItDown to convert compatible document formats (PDF, DOCX, etc.)",
)
def main(
    path: str,
    target_dir: str,
    branch: str,
    max_size: int,
    output: str,
    split_output: str,
    exclude_dir: tuple,
    include_ext: tuple,
    exclude_ext: tuple,
    url_mode: str,
    debug: bool,
    use_markitdown: bool,
):
    """Read and analyze documentation from a directory, repository, or URL"""
    try:
        # Validación: no permitir valores vacíos en --exclude-dir / -x
        for d in exclude_dir:
            if not d or d.strip() == "":
                raise click.UsageError(
                    "Empty value detected for --exclude-dir/-x. Please provide a valid directory name."
                )

        # Validamos que url_mode sea uno de los valores permitidos
        if url_mode not in ("full", "clean"):
            url_mode = "clean"  # Valor por defecto si no es válido

        # Mostrar al usuario la lista final de directorios excluidos
        final_exclude_dirs = DEFAULT_EXCLUDE_DIRS | set(exclude_dir)
        if exclude_dir:
            console.print(
                f"[yellow]Excluding directories:[/yellow] {', '.join(sorted(final_exclude_dirs))}"
            )

        config = ReadConfig(
            max_file_size=max_size,
            exclude_dirs=final_exclude_dirs,
            include_extensions=DEFAULT_INCLUDE_EXTENSIONS | set(include_ext),
            exclude_extensions=set(exclude_ext),
            target_dir=target_dir,
            url_mode=cast(
                URL_MODES, url_mode
            ),  # Usamos cast para que mypy entienda el tipo
            use_markitdown=use_markitdown,
            markitdown_extensions=MARKITDOWN_EXTENSIONS.copy()
            if use_markitdown
            else set(),
            debug=debug,
        )

        reader = Readium(config)
        if split_output:
            reader.split_output_dir = split_output

        summary, tree, content = reader.read_docs(path, branch=branch)

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(f"Summary:\n{summary}\n\n")
                f.write(f"Tree:\n{tree}\n\n")
                f.write(f"Content:\n{content}")
            console.print(f"[green]Results saved to {output}[/green]")
        else:
            console.print("[bold]Summary:[/bold]")
            console.print(summary)
            console.print("\n[bold]Tree:[/bold]")
            console.print(tree)
            console.print("\n[bold]Content:[/bold]")
            try:
                console.print(content)
            except Exception as e:
                # Handle unprintable content
                console.print(
                    "\n[red]Error displaying content on screen. Check the output file for details.[/red]"
                )
                if not output:
                    output = "output.txt"
                with open(output, "w", encoding="utf-8") as f:
                    f.write(f"Summary:\n{summary}\n\n")
                    f.write(f"Tree:\n{tree}\n\n")
                    f.write(f"Content:\n{content}")
                console.print(f"[green]Content saved to {output}[/green]")

    except Exception as e:
        print_error(console, str(e))
        raise click.Abort()


if __name__ == "__main__":
    main()
