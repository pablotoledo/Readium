from click.testing import CliRunner

from readium.cli import main


def test_help_includes_output_option():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert "-o, --output" in result.output
    assert "Output file path" in result.output
    assert "readium /path/to/directory -o output.md" in result.output  # Updated line


def test_help_includes_examples():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert "Examples:" in result.output
    assert "Process a local directory" in result.output
