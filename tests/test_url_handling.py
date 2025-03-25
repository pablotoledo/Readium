# tests/test_url_handling.py
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from readium import ReadConfig, Readium
from readium.core import convert_url_to_markdown, is_url


def test_is_url():
    """Test URL detection"""
    assert is_url("https://github.com")
    assert is_url("http://example.com/docs")
    assert not is_url("github.com")  # No scheme
    assert not is_url("/local/path")
    assert not is_url("git@github.com:user/repo.git")  # SSH URL
    assert not is_url("https://github.com/user/repo.git")  # Git URL


@patch("trafilatura.fetch_url")
@patch("trafilatura.extract")
@patch("trafilatura.extract_metadata")
def test_convert_url_to_markdown(mock_metadata, mock_extract, mock_fetch):
    """Test converting a URL to Markdown"""
    # Setup mocks
    mock_fetch.return_value = "<html><body><h1>Test</h1><p>Content</p></body></html>"
    mock_extract.return_value = "# Test\n\nContent"

    # Setup metadata mock
    metadata_mock = Mock()
    metadata_mock.title = "Test Page"
    mock_metadata.return_value = metadata_mock

    # Test conversion
    title, markdown = convert_url_to_markdown("https://example.com/docs")

    # Assertions
    assert title == "Test Page"
    assert markdown == "# Test\n\nContent"
    mock_fetch.assert_called_once_with("https://example.com/docs")
    mock_extract.assert_called_once()


@patch("readium.core.convert_url_to_markdown")
def test_read_docs_url(mock_convert):
    """Test reading a URL directly"""
    # Setup mock
    mock_convert.return_value = (
        "Test Document",
        "# Test Document\n\nThis is test content.",
    )

    # Setup reader
    reader = Readium(ReadConfig(debug=True))

    # Test URL processing
    summary, tree, content = reader.read_docs("https://example.com/documentation")

    # Assertions
    assert "URL processed: https://example.com/documentation" in summary
    assert "Title: Test Document" in summary
    assert "Documentation Structure:" in tree
    assert "documentation.md" in tree
    assert "# Test Document" in content
    assert "This is test content." in content


@patch("readium.core.convert_url_to_markdown")
def test_read_docs_url_with_output(mock_convert, tmp_path):
    """Test reading a URL with output file"""
    # Setup mock
    mock_convert.return_value = ("Test Document", "# Test Document\n\nContent.")

    # Setup reader with split output
    output_dir = tmp_path / "output"
    reader = Readium(ReadConfig(debug=True))
    reader.split_output_dir = str(output_dir)

    # Test URL processing
    summary, tree, content = reader.read_docs("https://example.com/page.html")

    # Assertions
    assert "Split files output directory:" in summary
    assert os.path.exists(output_dir)

    # Check if at least one file was created
    files = list(output_dir.glob("*.txt"))
    assert len(files) > 0

    # Check content of first file
    with open(files[0], "r", encoding="utf-8") as f:
        file_content = f.read()
        assert "Original Path:" in file_content
        assert "# Test Document" in file_content


@patch("trafilatura.fetch_url")
def test_convert_url_error_handling(mock_fetch):
    """Test error handling when fetching URL fails"""
    # Setup mock to return None (failed download)
    mock_fetch.return_value = None

    # Test with invalid URL
    with pytest.raises(ValueError) as excinfo:
        convert_url_to_markdown("https://example.com/nonexistent")

    assert "No se pudo descargar" in str(excinfo.value)


def test_cli_url_processing():
    """Test CLI with URL processing"""
    from click.testing import CliRunner

    from readium.cli import main

    # Patch convert_url_to_markdown to avoid actual network requests
    with patch("readium.core.convert_url_to_markdown") as mock_convert:
        mock_convert.return_value = ("Test Title", "# Test Content")

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                main,
                [
                    "https://example.com/docs",
                    "--output",
                    "docs.md",
                    "--url-mode",
                    "clean",
                ],
            )

            # Verify successful execution
            assert result.exit_code == 0
            assert "URL processed: https://example.com/docs" in result.output
            assert "Results saved to docs.md" in result.output

            # Check if file was created
            assert os.path.exists("docs.md")
