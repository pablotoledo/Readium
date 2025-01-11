import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from .config import (DEFAULT_EXCLUDE_DIRS, DEFAULT_EXCLUDE_FILES,
                     DEFAULT_INCLUDE_EXTENSIONS)
from markitdown import MarkItDown, FileConversionException, UnsupportedFormatException


def is_git_url(url: str) -> bool:
    """Check if the given string is a git URL"""
    return url.startswith(("http://", "https://")) and (
        url.endswith(".git") or "github.com" in url or "gitlab.com" in url
    )


def clone_repository(url: str, target_dir: str) -> None:
    """Clone a git repository to the target directory"""
    try:
        subprocess.run(
            ["git", "clone", "--depth=1", url, target_dir],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to clone repository: {e.stderr.decode()}")


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
    use_markitdown: bool = False
    markitdown_extensions: Optional[Set[str]] = None
    debug: bool = False  # Add this line to include the debug attribute


class Readium:
    """Main class for reading documentation"""

    def __init__(self, config: Optional[ReadConfig] = None):
        self.config = config or ReadConfig()
        self.markitdown = MarkItDown() if self.config.use_markitdown else None

    def log_debug(self, msg: str) -> None:
        """Print debug messages if debug mode is enabled"""
        if self.config.debug:
            print(f"DEBUG: {msg}")

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
        file_ext = os.path.splitext(file_path)[1].lower()
        
        self.log_debug(f"Checking file: {file_path}")
        
        # Check exclude patterns - handle macOS @ suffix
        base_name = str(file_path.name).rstrip('@')
        if any(pattern in base_name for pattern in self.config.exclude_files):
            self.log_debug(f"Excluding {file_path} due to exclude patterns")
            return False

        # Check size
        file_size = file_path.stat().st_size
        if file_size > self.config.max_file_size:
            self.log_debug(f"Excluding {file_path} due to size: {file_size} > {self.config.max_file_size}")
            return False

        if self.config.use_markitdown:
            # Si markitdown está activo y se especificaron extensiones, usar solo esas
            if self.config.markitdown_extensions:
                if file_ext in self.config.markitdown_extensions:
                    self.log_debug(f"Including {file_path} for markitdown processing")
                    return True
                self.log_debug(f"Extension {file_ext} not in markitdown extensions: {self.config.markitdown_extensions}")
            else:
                # Si no se especificaron extensiones, intentar usar markitdown para todo
                try:
                    self.markitdown.convert(str(file_path))
                    self.log_debug(f"Including {file_path} for markitdown processing (auto-detected)")
                    return True
                except (FileConversionException, UnsupportedFormatException) as e:
                    self.log_debug(f"Markitdown couldn't process {file_path}: {str(e)}")
                    pass

        # Si no se usa markitdown o el archivo no es compatible con markitdown,
        # verificar si está en las extensiones incluidas
        supported_extensions = self.config.include_extensions | (self.config.markitdown_extensions or set())
        if not any(str(file_path).lower().endswith(ext) for ext in supported_extensions):
            self.log_debug(f"Extension {file_ext} not in supported extensions: {supported_extensions}")
            return False

        # Solo verificar si es binario para archivos que no son de markitdown
        if file_ext not in (self.config.markitdown_extensions or set()):
            is_bin = self.is_binary(file_path)
            if is_bin:
                self.log_debug(f"Excluding {file_path} because it's binary")
                return False
            
        self.log_debug(f"Including {file_path} for processing")
        return True
     
    def read_docs(self, path: Union[str, Path]) -> Tuple[str, str, str]:
        """
        Read documentation from a directory or git repository

        Parameters
        ----------
        path : Union[str, Path]
            Local path or git URL

        Returns
        -------
        Tuple[str, str, str]:
            summary, tree structure, content
        """
        # If it's a git URL, clone first
        if isinstance(path, str) and is_git_url(path):
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    clone_repository(path, temp_dir)
                    return self._process_directory(Path(temp_dir))
                except Exception as e:
                    raise ValueError(f"Error processing git repository: {str(e)}")
        else:
            path = Path(path)
            if not path.exists():
                raise ValueError(f"Path does not exist: {path}")
            return self._process_directory(path)

    def _process_file(self, file_path: Path, relative_path: Path) -> Optional[dict]:
        """Process a single file, using markitdown if enabled"""
        self.log_debug(f"Processing file: {file_path}")
        
        try:
            if self.config.use_markitdown:
                file_ext = os.path.splitext(file_path)[1].lower()
                if not self.config.markitdown_extensions or file_ext in self.config.markitdown_extensions:
                    try:
                        self.log_debug(f"Attempting to process with markitdown")
                        result = self.markitdown.convert(str(file_path))
                        self.log_debug("Successfully processed with markitdown")
                        return {
                            "path": str(relative_path),
                            "content": result.text_content
                        }
                    except (FileConversionException, UnsupportedFormatException) as e:
                        self.log_debug(f"MarkItDown couldn't process {file_path}: {str(e)}")
                    except Exception as e:
                        self.log_debug(f"Error with MarkItDown processing {file_path}: {str(e)}")

            # Fall back to normal reading
            self.log_debug("Attempting normal file reading")
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                self.log_debug("Successfully read file normally")
                return {
                    "path": str(relative_path),
                    "content": content
                }
        except Exception as e:
            self.log_debug(f"Error processing file: {str(e)}")
            return None

    def _process_directory(self, path: Path) -> Tuple[str, str, str]:
        """Internal method to process a directory"""
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
                    relative_path = file_path.relative_to(path)
                    result = self._process_file(file_path, relative_path)
                    if result:
                        files.append(result)

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
        if self.config.use_markitdown:
            summary += "Using MarkItDown for compatible files\n"
            if self.config.markitdown_extensions:
                summary += f"MarkItDown extensions: {', '.join(self.config.markitdown_extensions)}\n"

        return summary, tree, content
