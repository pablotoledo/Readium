from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .config import (
    DEFAULT_EXCLUDE_DIRS,
    DEFAULT_INCLUDE_EXTENSIONS,
    MARKITDOWN_EXTENSIONS,
)
from .core import ReadConfig, Readium
from .utils.error_handling import print_error

console = Console()


@click.command(
    help="""
Read and analyze documentation from directories or repositories.

Examples:
    # Process a local directory
    readium /path/to/directory

    # Process a Git repository
    readium https://github.com/username/repository

    # Process a specific branch of a Git repository
    readium https://github.com/username/repository -b feature-branch

    # Save output to a file
    readium /path/to/directory -o output.md

    # Process specific subdirectory
    readium /path/to/directory -t python
"""
)
@click.argument("path", type=str)
@click.option("--target-dir", "-t", help="Target subdirectory to analyze")
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
    "--output",
    "-o",
    type=click.Path(),
    help="""Output file path. If specified, the results will be saved to this file
    instead of displaying in the terminal. For example:
    readium input.md -o output.md""",
)
@click.option(
    "--exclude-dir", "-x", multiple=True, help="Additional directories to exclude"
)
@click.option(
    "--include-ext", "-i", multiple=True, help="Additional extensions to include"
)
@click.option(
    "--use-markitdown/--no-markitdown",
    "-m/-M",
    default=False,
    help="Use MarkItDown for compatible file formats",
)
@click.option(
    "--markitdown-ext",
    "-k",
    multiple=True,
    help="Specific extensions to process with MarkItDown (default: all supported)",
)
@click.option(
    "--debug/--no-debug",
    "-d/-D",
    default=False,
    help="Enable debug mode",
)
def main(
    path: str,
    target_dir: str,
    branch: str,
    max_size: int,
    output: str,
    exclude_dir: tuple,
    include_ext: tuple,
    use_markitdown: bool,
    markitdown_ext: tuple,
    debug: bool,
):
    """Read and analyze documentation from a directory or repository"""
    try:
        config = ReadConfig(
            max_file_size=max_size,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS | set(exclude_dir),
            include_extensions=DEFAULT_INCLUDE_EXTENSIONS | set(include_ext),
            target_dir=target_dir,
            use_markitdown=use_markitdown,
            markitdown_extensions=(
                set(markitdown_ext) if markitdown_ext else MARKITDOWN_EXTENSIONS
            ),
            debug=debug,
        )

        reader = Readium(config)
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
