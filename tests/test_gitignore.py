import os
from pathlib import Path
from readium.core import Readium, ReadConfig

def test_gitignore_respect(tmp_path):
    """Test that files in .gitignore are ignored by default"""
    # Create a test directory structure
    (tmp_path / "ignored_dir").mkdir()
    (tmp_path / "included_dir").mkdir()
    
    (tmp_path / "ignored.txt").write_text("ignored")
    (tmp_path / "included.txt").write_text("included")
    (tmp_path / "ignored_dir" / "file.txt").write_text("ignored")
    (tmp_path / "included_dir" / "file.txt").write_text("included")
    
    # Create .gitignore
    (tmp_path / ".gitignore").write_text("ignored.txt\nignored_dir/")
    
    # Run Readium
    config = ReadConfig()
    reader = Readium(config)
    summary, tree, content = reader.read_docs(tmp_path)
    
    # Check results
    assert "included.txt" in tree
    assert "included_dir/file.txt" in tree
    assert "ignored.txt" not in tree
    assert "ignored_dir/file.txt" not in tree

def test_gitignore_ignore(tmp_path):
    """Test that .gitignore is ignored when use_gitignore is False"""
    # Create a test directory structure
    (tmp_path / "ignored_dir").mkdir()
    (tmp_path / "included_dir").mkdir()
    
    (tmp_path / "ignored.txt").write_text("ignored")
    (tmp_path / "included.txt").write_text("included")
    (tmp_path / "ignored_dir" / "file.txt").write_text("ignored")
    (tmp_path / "included_dir" / "file.txt").write_text("included")
    
    # Create .gitignore
    (tmp_path / ".gitignore").write_text("ignored.txt\nignored_dir/")
    
    # Run Readium with use_gitignore=False
    config = ReadConfig(use_gitignore=False)
    reader = Readium(config)
    summary, tree, content = reader.read_docs(tmp_path)
    
    # Check results
    assert "included.txt" in tree
    assert "included_dir/file.txt" in tree
    assert "ignored.txt" in tree
    assert "ignored_dir/file.txt" in tree

def test_nested_gitignore(tmp_path):
    """Test that nested .gitignore files are respected (if implemented) or at least don't crash"""
    # Note: Current implementation only checks root .gitignore. 
    # This test verifies that we don't crash and behave predictably (ignoring nested gitignore for now or respecting it if pathspec handles it)
    # Since we only load from root, nested gitignores won't be respected unless we change implementation.
    # So we expect nested ignored files to be INCLUDED if they are not in root .gitignore.
    
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "nested_ignored.txt").write_text("ignored")
    (tmp_path / "subdir" / ".gitignore").write_text("nested_ignored.txt")
    
    config = ReadConfig()
    reader = Readium(config)
    summary, tree, content = reader.read_docs(tmp_path)
    
    # With current implementation (root only), this file should be present
    assert "nested_ignored.txt" in tree
