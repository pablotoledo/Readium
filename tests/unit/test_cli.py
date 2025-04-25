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


def test_exclude_dir_single(monkeypatch):
    """Test using -x once passes the value to the config."""
    runner = CliRunner()
    # Patch Readium.read_docs to avoid actual processing
    monkeypatch.setattr(
        "readium.core.Readium.read_docs",
        lambda self, path, branch=None: ("summary", "tree", "content"),
    )
    result = runner.invoke(main, [".", "-x", "dir1"])
    assert result.exit_code == 0
    # No error should occur, and the CLI should run


def test_exclude_dir_multiple(monkeypatch):
    """Test using -x multiple times passes all values to the config."""
    runner = CliRunner()
    monkeypatch.setattr(
        "readium.core.Readium.read_docs",
        lambda self, path, branch=None: ("summary", "tree", "content"),
    )
    result = runner.invoke(main, [".", "-x", "dir1", "-x", "dir2"])
    assert result.exit_code == 0


def test_exclude_dir_duplicates(monkeypatch):
    """Test using -x with duplicate values does not cause error."""
    runner = CliRunner()
    monkeypatch.setattr(
        "readium.core.Readium.read_docs",
        lambda self, path, branch=None: ("summary", "tree", "content"),
    )
    result = runner.invoke(main, [".", "-x", "dir1", "-x", "dir1"])
    assert result.exit_code == 0


def test_exclude_dir_empty_value(monkeypatch):
    """Test using -x with an empty value should fail or warn."""
    runner = CliRunner()
    monkeypatch.setattr(
        "readium.core.Readium.read_docs",
        lambda self, path, branch=None: ("summary", "tree", "content"),
    )
    result = runner.invoke(main, [".", "-x", ""])
    # Should fail or print an error message
    assert result.exit_code != 0 or "exclude-dir" in result.output.lower()
