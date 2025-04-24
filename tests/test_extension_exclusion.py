import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from readium.cli import main
from readium.config import ReadConfig
from readium.core import Readium


@pytest.fixture
def temp_dir_with_files():
    """Create a temporary directory with test files of various extensions"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir)
        # Create test files with different extensions
        files = {
            "doc1.md": "# Test Markdown",
            "doc2.txt": "Plain text file",
            "code.py": "def test(): pass",
            "config.json": '{"key": "value"}',
            "data.yml": "key: value",
            "styles.css": "body { color: black; }",
        }
        for name, content in files.items():
            file_path = path / name
            file_path.write_text(content)
        yield path


def test_exclude_extensions_basic(temp_dir_with_files):
    """Test basic exclusion of a single file extension"""
    config = ReadConfig(exclude_extensions={".json"})
    reader = Readium(config)
    summary, tree, content = reader.read_docs(temp_dir_with_files)
    assert "Files processed:" in summary
    assert "doc1.md" in tree
    assert "code.py" in tree
    assert "config.json" not in tree
    assert "# Test Markdown" in content
    assert "def test():" in content
    assert '"key": "value"' not in content


def test_exclude_extensions_multiple(temp_dir_with_files):
    """Test exclusion of multiple file extensions"""
    config = ReadConfig(exclude_extensions={".json", ".yml"})
    reader = Readium(config)
    summary, tree, content = reader.read_docs(temp_dir_with_files)
    assert "Files processed:" in summary
    assert "doc1.md" in tree
    assert "code.py" in tree
    assert "config.json" not in tree
    assert "data.yml" not in tree
    # .css is not in default include_extensions, so it should not be in tree


def test_exclude_and_include_extensions(temp_dir_with_files):
    """Test interaction between include and exclude extensions"""
    config = ReadConfig(
        include_extensions={".md", ".json"}, exclude_extensions={".json"}
    )
    reader = Readium(config)
    summary, tree, content = reader.read_docs(temp_dir_with_files)
    assert "Files processed:" in summary
    assert "doc1.md" in tree
    assert "code.py" not in tree
    assert "config.json" not in tree
    assert "data.yml" not in tree
    assert "styles.css" not in tree
    assert "# Test Markdown" in content


def test_case_insensitive_extension_matching(temp_dir_with_files):
    """Test that extension exclusion is case-insensitive"""
    uppercase_file = temp_dir_with_files / "test.JSON"
    uppercase_file.write_text('{"uppercase": true}')
    config = ReadConfig(exclude_extensions={".json"})
    reader = Readium(config)
    summary, tree, content = reader.read_docs(temp_dir_with_files)
    assert "config.json" not in tree
    assert "test.JSON" not in tree


def test_cli_exclude_extensions(temp_dir_with_files):
    """Test CLI interface with exclude-ext option"""
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            str(temp_dir_with_files),
            "--exclude-ext",
            ".json",
            "--exclude-ext",
            ".yml",
            "--debug",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    # Extract the "Tree" section from output for assertions
    tree_start = result.output.find("Tree:")
    content_start = result.output.find("Content:")
    tree_section = (
        result.output[tree_start:content_start]
        if tree_start != -1 and content_start != -1
        else result.output
    )
    assert "doc1.md" in tree_section
    assert "code.py" in tree_section
    assert "config.json" not in tree_section
    assert "data.yml" not in tree_section


@patch("readium.core.clone_repository")
def test_exclude_extensions_with_git(mock_clone, temp_dir_with_files):
    """Test extension exclusion with git repositories"""
    mock_clone.side_effect = lambda url, target_dir, branch=None: None
    config = ReadConfig(exclude_extensions={".json"})
    reader = Readium(config)
    with patch.object(reader, "_process_directory") as mock_process:
        mock_process.return_value = (
            "Summary",
            "Tree without config.json",
            "Content without JSON",
        )
        summary, tree, content = reader.read_docs("https://github.com/fake/repo.git")
        mock_process.assert_called_once()
        assert reader.config.exclude_extensions == {".json"}


def test_exclude_all_extensions(temp_dir_with_files):
    """Test excluding all file extensions to ensure no files are processed"""
    all_extensions = {
        os.path.splitext(f)[1].lower()
        for f in os.listdir(temp_dir_with_files)
        if "." in f
    }
    config = ReadConfig(exclude_extensions=all_extensions)
    reader = Readium(config)
    summary, tree, content = reader.read_docs(temp_dir_with_files)
    assert "Files processed: 0" in summary
    assert "Documentation Structure:" in tree
    assert len(content.strip()) == 0
