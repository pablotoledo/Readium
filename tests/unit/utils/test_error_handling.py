import io

from rich.console import Console

from readium.utils.error_handling import print_error


def test_print_error_normal():
    console = Console(file=io.StringIO(), force_terminal=True)
    print_error(console, "Normal error")
    assert "Normal error" in console.file.getvalue()


def test_print_error_with_markup():
    console = Console(file=io.StringIO(), force_terminal=True)
    print_error(console, "Error with [tags]")
    output = console.file.getvalue()
    assert "Error:" in output
    assert "Error with" in output


def test_print_error_with_rich_markup():
    console = Console(file=io.StringIO(), force_terminal=True)
    print_error(console, "[red]Formatted[/red]")
    output = console.file.getvalue()
    assert "Error:" in output
    assert "Formatted" in output
