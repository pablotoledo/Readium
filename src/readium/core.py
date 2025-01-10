import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from .config import (
    DEFAULT_EXCLUDE_DIRS,
    DEFAULT_EXCLUDE_FILES,
    DEFAULT_INCLUDE_EXTENSIONS,
)


@dataclass
class ReadConfig:
    """Configuration for document reading"""

    max_file_size: int = 1024 * 1024  # 1MB default
    exclude_dirs: Set[str] = field(default_factory=lambda: DEFAULT_EXCLUDE_DIRS.copy())
    exclude_files: Set[str] = field(
        default_factory=lambda: DEFAULT_EXCLUDE_FILES.copy()
    )
    include_extensions: Set[str] = field(
        default_factory=lambda: DEFAULT_INCLUDE_EXTENSIONS.copy()
    )
    target_dir: Optional[str] = None


class Readium:
    """Main class for reading documentation"""

    def __init__(self, config: Optional[ReadConfig] = None):
        self.config = config or ReadConfig()

    def is_binary(self, file_path: Union[str, Path]) -> bool:
        """Check if a file is binary"""
        try:
            with open(file_path, "rb") as file:
                chunk = file.read(1024)
                return bool(
                    chunk.translate(
                        None,
                        bytes([7, 8, 9, 10, 12, 13, 27] + list(range(0x20, 0x100))),
                    )
                )
        except Exception:
            return True

    def should_process_file(self, file_path: Union[str, Path]) -> bool:
        """Determine if a file should be processed based on configuration"""
        file_path = Path(file_path)

        # Check size
        if file_path.stat().st_size > self.config.max_file_size:
            return False

        # Check extension
        if not any(
            str(file_path).lower().endswith(ext)
            for ext in self.config.include_extensions
        ):
            return False

        # Check exclude patterns
        if any(pattern in str(file_path) for pattern in self.config.exclude_files):
            return False

        # Check if binary
        if self.is_binary(file_path):
            return False

        return True

    def read_docs(self, path: Union[str, Path]) -> Tuple[str, str, str]:
        """
        Read documentation from a directory

        Returns:
        --------
        Tuple[str, str, str]:
            summary, tree structure, content
        """
        path = Path(path)
        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")

        files = []

        # If target_dir is specified, look only in that subdirectory
        if self.config.target_dir:
            base_path = path / self.config.target_dir
            if not base_path.exists():
                raise ValueError(
                    f"Target directory not found: {self.config.target_dir}"
                )
            path = base_path

        for root, dirs, filenames in os.walk(path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in self.config.exclude_dirs]

            for filename in filenames:
                file_path = Path(root) / filename

                if self.should_process_file(file_path):
                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read()
                            files.append(
                                {
                                    "path": str(file_path.relative_to(path)),
                                    "content": content,
                                }
                            )
                    except Exception as e:
                        print(f"Error reading {file_path}: {str(e)}")

        # Generate tree
        tree = "Documentation Structure:\n"
        for file in files:
            tree += f"└── {file['path']}\n"

        # Generate content
        content = "\n\n".join(
            [
                f"================================================\n"
                f"File: {f['path']}\n"
                f"================================================\n"
                f"{f['content']}"
                for f in files
            ]
        )

        # Generate summary
        summary = f"Path analyzed: {path}\n"
        summary += f"Files processed: {len(files)}\n"
        if self.config.target_dir:
            summary += f"Target directory: {self.config.target_dir}\n"

        return summary, tree, content
