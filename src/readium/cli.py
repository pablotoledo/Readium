
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from .core import Readium, ReadConfig
from .config import DEFAULT_EXCLUDE_DIRS, DEFAULT_INCLUDE_EXTENSIONS

console = Console()

@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--target-dir', '-t', help='Target subdirectory to analyze')
@click.option('--max-size', '-s', type=int, default=1024*1024, 
              help='Maximum file size in bytes (default: 1MB)')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--exclude-dir', '-x', multiple=True, help='Additional directories to exclude')
@click.option('--include-ext', '-i', multiple=True, help='Additional extensions to include')
def main(path: str, target_dir: str, max_size: int, output: str,
         exclude_dir: tuple, include_ext: tuple):
    """Read and analyze documentation from a directory or repository"""
    try:
        config = ReadConfig(
            max_file_size=max_size,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS | set(exclude_dir),
            include_extensions=DEFAULT_INCLUDE_EXTENSIONS | set(include_ext),
            target_dir=target_dir
        )
        
        reader = Readium(config)
        summary, tree, content = reader.read_docs(path)
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
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
            console.print(content)
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.Abort()

if __name__ == '__main__':
    main()
