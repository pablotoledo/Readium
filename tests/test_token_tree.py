import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from readium import ReadConfig, Readium
from readium.cli import main


@pytest.fixture
def temp_dir_with_files():
    """Create a temporary directory with test files for token counting"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir)
        docs_dir = path / "docs"
        src_dir = path / "src"
        docs_dir.mkdir()
        src_dir.mkdir()
        files = {
            "README.md": "# Test Project\nThis is a test project for token counting.",
            "docs/guide.md": "# User Guide\n\n" + "This is test content.\n" * 10,
            "docs/api.md": "# API Reference\n\n" + "API details here.\n" * 15,
            "src/main.py": "def main():\n    print('Hello world')\n\nif __name__ == '__main__':\n    main()",
        }
        for rel_path, content in files.items():
            file_path = path / rel_path
            file_path.parent.mkdir(exist_ok=True)
            file_path.write_text(content)
        yield path


def test_estimate_tokens_tiktoken():
    """Test token estimation with tiktoken method (único disponible)"""
    config = ReadConfig()
    reader = Readium(config)
    assert reader.estimate_tokens("This is a test") > 0
    assert reader.estimate_tokens("") == 0


def test_generate_token_tree(temp_dir_with_files):
    """Test token tree generation"""
    config = ReadConfig(show_token_tree=True)
    reader = Readium(config)
    with patch.object(reader, "estimate_tokens", return_value=100):
        files = [
            {"path": "README.md", "content": "Test content"},
            {"path": "docs/guide.md", "content": "Guide content"},
            {"path": "docs/api.md", "content": "API content"},
            {"path": "src/main.py", "content": "Python code"},
        ]
        token_tree = reader.generate_token_tree(files, temp_dir_with_files)
        assert "# Directory Token Tree" in token_tree
        assert "docs" in token_tree
        assert "src" in token_tree
        assert "README.md" in token_tree
        assert "guide.md" in token_tree
        assert "api.md" in token_tree
        assert "main.py" in token_tree
        assert "100" in token_tree
        assert "Total Files:" in token_tree
        assert "Total Tokens:" in token_tree


def test_read_docs_with_token_tree(temp_dir_with_files):
    """Test integration of token tree with read_docs"""
    config = ReadConfig(show_token_tree=True)
    reader = Readium(config)
    summary, tree, content = reader.read_docs(temp_dir_with_files)
    # When show_token_tree is True, tree should be empty or just the header
    assert tree.strip() == "" or tree.strip().startswith("Documentation Structure:")


def test_cli_with_token_tree(temp_dir_with_files):
    """Test CLI with token tree option using both methods"""
    runner = CliRunner()
    # Test with flag
    result_flag = runner.invoke(main, [str(temp_dir_with_files), "--tokens"])
    assert "# Directory Token Tree" in result_flag.output
    assert result_flag.exit_code == 0
    # Test with subcommand
    result_cmd = runner.invoke(main, ["tokens", str(temp_dir_with_files)])
    assert "# Directory Token Tree" in result_cmd.output
    assert result_cmd.exit_code == 0
    # Output should be identical
    assert result_flag.output == result_cmd.output


def test_backward_compatibility():
    """Test that old functionality still works without token tree"""
    config = ReadConfig()
    reader = Readium(config)
    with patch.object(reader, "generate_token_tree") as mock_generate:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir)
            (path / "file.md").write_text("Test content")
            reader.read_docs(path)
            assert mock_generate.called


def test_url_with_token_tree():
    """Test token tree works with URLs"""
    config = ReadConfig(show_token_tree=True)
    reader = Readium(config)
    with patch("readium.core.convert_url_to_markdown") as mock_convert:
        mock_convert.return_value = ("Test Document", "# Test Content")
        summary, tree, content = reader.read_docs("https://example.com/docs")
        assert "Token Tree generated" in summary
        assert "# Directory Token Tree" in tree
