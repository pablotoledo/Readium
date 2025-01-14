import rich.errors
from rich.console import Console


def print_error(console: Console, message: str) -> None:
    """Safely print error messages that might contain markup-like content.

    Args:
        console: Rich console instance for output
        message: Error message that might contain markup-like content
    """
    try:
        console.print(f"[red]Error: {message}[/red]")
    except rich.errors.MarkupError:
        # Fallback to plain text if markup fails
        console.print(f"Error: {message}", style="red", markup=False)
