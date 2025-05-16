import os
from pathlib import Path

from click.testing import CliRunner

from readium.cli import main


def test_tokens_command_basic(tmp_path):
    (tmp_path / "a.md").write_text("One two three four five")
    (tmp_path / "b.txt").write_text("Six seven eight nine ten eleven")
    runner = CliRunner()
    result = runner.invoke(main, ["tokens", str(tmp_path)])
    assert result.exit_code == 0
    assert "# Directory Token Tree" in result.output
    assert "a.md" in result.output
    assert "b.txt" in result.output
    assert "Total Tokens" in result.output


def test_tokens_command_exclude_ext(tmp_path):
    (tmp_path / "a.md").write_text("One two three four five")
    (tmp_path / "b.txt").write_text("Six seven eight nine ten eleven")
    runner = CliRunner()
    result = runner.invoke(main, ["tokens", str(tmp_path), "--exclude-ext", ".md"])
    assert result.exit_code == 0
    assert "a.md" not in result.output
    assert "b.txt" in result.output


def test_tokens_command_empty_dir(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["tokens", str(tmp_path)])
    assert result.exit_code == 0
    assert "Total Files: 0" in result.output or "Total Files:** 0" in result.output
