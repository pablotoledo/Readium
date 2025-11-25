import tempfile
from pathlib import Path

from click.testing import CliRunner

from readium.cli import main


def test_exclude_dir_with_relative_path():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir)
        (path / "skip").mkdir()
        (path / "skip" / "a.md").write_text("skip")
        (path / "keep.md").write_text("keep")

        runner = CliRunner()
        result = runner.invoke(main, [str(path), "-x", "./skip"])
        assert result.exit_code == 0
        # Tree section should not list files inside 'skip'
        tree_start = result.output.find("Tree:")
        content_start = result.output.find("Content:")
        tree_section = (
            result.output[tree_start:content_start]
            if tree_start != -1 and content_start != -1
            else result.output
        )
        assert "skip" not in tree_section
        assert "keep.md" in tree_section
