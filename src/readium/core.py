import os
import subprocess
import tempfile
import urllib.parse
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from markitdown import FileConversionException, MarkItDown, UnsupportedFormatException

from .config import (
    DEFAULT_EXCLUDE_DIRS,
    DEFAULT_EXCLUDE_FILES,
    DEFAULT_INCLUDE_EXTENSIONS,
    MARKITDOWN_EXTENSIONS,
    ReadConfig,
)


def is_git_url(url: str) -> bool:
    """Check if the given string is a git URL"""
    if not url.startswith(("http://", "https://")):
        return False

    # Detect Git-specific URLs
    if url.endswith(".git"):
        return True

    # Detect GitHub/GitLab style paths
    if "github.com/" in url or "gitlab.com/" in url:
        parts = url.split("/")
        # Basic user/repo format (at least 4 parts)
        if len(parts) >= 4:
            return True

    return False


def is_url(url: str) -> bool:
    """Check if a string is a valid URL (but not a git URL)"""
    try:
        result = urllib.parse.urlparse(url)
        # It is an HTTP/HTTPS URL but NOT a git URL
        is_valid_url = all([result.scheme, result.netloc]) and result.scheme in (
            "http",
            "https",
        )
        return is_valid_url and not is_git_url(url)
    except ValueError:
        return False


def convert_url_to_markdown(
    url: str, config: Optional[ReadConfig] = None
) -> Tuple[str, str]:
    """
    Convert a URL to Markdown using trafilatura

    Parameters
    ----------
    url : str
        URL to convert.
    config : Optional[ReadConfig]
        Configuration for processing, defaults to None

    Returns
    -------
    Tuple[str, str]:
        Extracted title, content in Markdown format.
    """
    if config is None:
        config = ReadConfig()

    try:
        # Attempt to import trafilatura here to handle import errors
        import trafilatura
        from trafilatura.settings import use_config

        # Configure trafilatura for Markdown output
        trafilatura_config = use_config()
        trafilatura_config.set("DEFAULT", "output_format", "markdown")

        # Adjust extraction settings based on URL mode
        if config.url_mode == "full":
            # Disable aggressive filtering
            trafilatura_config.set("DEFAULT", "extraction_timeout", "30")
            trafilatura_config.set("DEFAULT", "min_extracted_size", "10")
            trafilatura_config.set(
                "EXTRACTION",
                "list_tags",
                "p, blockquote, q, dl, ul, ol, h1, h2, h3, h4, h5, h6, div, section, article",
            )

        # Download and extract content
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            raise ValueError(f"Failed to download content from {url}")

        # Extract metadata and content
        metadata = trafilatura.extract_metadata(downloaded)
        title = metadata.title if metadata and metadata.title else "Untitled"

        # Extract content as Markdown
        markdown = trafilatura.extract(
            downloaded,
            output_format="markdown",
            include_tables=config.include_tables,
            include_images=config.include_images,
            include_links=config.include_links,
            include_comments=config.include_comments,
            config=trafilatura_config,
        )

        if not markdown:
            raise ValueError(f"Failed to extract content from {url}")

        return title, markdown

    except ImportError:
        # If trafilatura is not installed, return an error message
        print(
            "Warning: Trafilatura is not installed. URL to Markdown conversion is disabled."
        )
        # Return generic error content
        return (
            "Error",
            f"# Error\n\nUnable to convert URL: {url}. The required package 'trafilatura' is not installed.",
        )
    except Exception as e:
        raise ValueError(f"Error converting URL to Markdown: {str(e)}")


def clone_repository(url: str, target_dir: str, branch: Optional[str] = None) -> None:
    """Clone a git repository to the target directory

    Parameters
    ----------
    url : str
        Repository URL
    target_dir : str
        Target directory for cloning
    branch : Optional[str]
        Specific branch to clone (default: None, uses default branch)
    """
    try:
        # Base command
        cmd = ["git", "clone", "--depth=1"]

        # Add branch specification if provided
        if branch:
            cmd.extend(["-b", branch])

        # If the URL contains '@', it is likely to have a token
        if "@" in url:
            # Extract the token and reconstruct the URL
            parts = url.split("@")
            token = parts[0].split("://")[-1]
            base_url = "://".join(parts[0].split("://")[:-1])
            repo_url = f"{base_url}://{parts[1]}"

            # Log for debugging (hiding the full token)
            token_preview = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "****"
            print(f"DEBUG: Attempting to clone with token: {token_preview}")
            if branch:
                print(f"DEBUG: Using branch: {branch}")

            # Use the token as a password with an empty username
            env = os.environ.copy()
            env["GIT_ASKPASS"] = "echo"
            env["GIT_USERNAME"] = ""
            env["GIT_PASSWORD"] = token

            cmd.extend([repo_url, target_dir])
            subprocess.run(cmd, check=True, capture_output=True, env=env)
        else:
            cmd.extend([url, target_dir])
            subprocess.run(cmd, check=True, capture_output=True)

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode()
        # Hide the token in the error message if present
        if "@" in url:
            parts = url.split("@")
            token = parts[0].split("://")[-1]
            error_msg = error_msg.replace(token, "****")
        raise ValueError(f"Failed to clone repository: {error_msg}")


class Readium:
    """Main class for reading documentation"""

    def __init__(self, config: Optional[ReadConfig] = None):
        self.config = config or ReadConfig()
        self.markitdown = MarkItDown() if self.config.use_markitdown else None
        self.branch: Optional[str] = None
        self.split_output_dir: Optional[str] = None

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
        path = Path(file_path)
        file_ext = os.path.splitext(str(path))[1].lower()

        self.log_debug(f"Checking file: {path}")

        # First check if the file is in an excluded directory
        parts = path.parts
        for excluded_dir in self.config.exclude_dirs:
            if excluded_dir in parts:
                self.log_debug(
                    f"Excluding {path} due to being in excluded directory {excluded_dir}"
                )
                return False

        # Check exclude patterns - handle macOS @ suffix
        base_name = path.name.rstrip("@")
        if any(pattern in base_name for pattern in self.config.exclude_files):
            self.log_debug(f"Excluding {path} due to exclude patterns")
            return False

        # NEW: Check if the file extension is in the excluded extensions (case-insensitive)
        if file_ext in {ext.lower() for ext in self.config.exclude_extensions}:
            self.log_debug(f"Excluding {path} due to excluded extension {file_ext}")
            return False

        # Check size
        if self.config.max_file_size >= 0:
            try:
                file_size = path.stat().st_size
                if file_size > self.config.max_file_size:
                    self.log_debug(
                        f"Excluding {path} due to size: {file_size} > {self.config.max_file_size}"
                    )
                    return False
            except FileNotFoundError:
                return False

        should_use_markitdown = (
            self.config.use_markitdown
            and self.config.markitdown_extensions is not None
            and file_ext in self.config.markitdown_extensions
        )

        if should_use_markitdown:
            self.log_debug(f"Including {path} for markitdown processing")
            return True

        # If not using markitdown or file isn't compatible with markitdown,
        # check if it's in the included extensions
        if file_ext not in self.config.include_extensions:
            self.log_debug(f"Extension {file_ext} not in supported extensions")
            return False

        # Check if binary only for non-markitdown files
        if not should_use_markitdown:
            is_bin = self.is_binary(path)
            if is_bin:
                self.log_debug(f"Excluding {path} because it's binary")
                return False

        self.log_debug(f"Including {path} for processing")
        return True

    def read_docs(
        self, path: Union[str, Path], branch: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """
        Read documentation from a directory, git repository, or URL

        Parameters
        ----------
        path : Union[str, Path]
            Local path, git URL, or web URL
        branch : Optional[str]
            Specific branch to clone for git repositories (default: None)

        Returns
        -------
        Tuple[str, str, str]:
            summary, tree structure, content
        """
        self.branch = branch

        # If it's a git URL, clone first
        if isinstance(path, str) and is_git_url(path):
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    clone_repository(path, temp_dir, branch)
                    return self._process_directory(Path(temp_dir), original_path=path)
                except Exception as e:
                    raise ValueError(f"Error processing git repository: {str(e)}")
        # If it's a regular URL, process it
        elif isinstance(path, str) and is_url(path):
            try:
                self.log_debug(f"URL detected: {path}")

                # Extract title and Markdown content
                title, markdown_content = convert_url_to_markdown(path, self.config)

                # Generate file name from the URL
                file_name = (
                    os.path.basename(urllib.parse.urlparse(path).path) or "index.md"
                )
                if not file_name.endswith(".md"):
                    file_name += ".md"

                # Generate result
                file_info = [
                    {"path": file_name, "content": markdown_content, "title": title}
                ]

                # Write split files if output directory is specified
                if self.split_output_dir:
                    self.write_split_files(
                        file_info, Path(urllib.parse.urlparse(path).netloc)
                    )

                # Generate tree structure
                tree = "Documentation Structure:\n"
                tree += f"└── {file_name} (from {path})\n"

                # Generate content
                content = f"================================================\n"
                content += f"File: {file_name}\n"
                content += f"Source: {path}\n"
                content += f"Title: {title}\n"
                content += f"================================================\n\n"
                content += markdown_content

                # Generate summary
                summary = f"URL processed: {path}\n"
                summary += f"Title: {title}\n"
                summary += f"Output file: {file_name}\n"
                if self.split_output_dir:
                    summary += (
                        f"Split files output directory: {self.split_output_dir}\n"
                    )

                return summary, tree, content

            except Exception as e:
                raise ValueError(f"Error processing URL: {str(e)}")
        else:
            path_obj = Path(path)
            if not path_obj.exists():
                raise ValueError(f"Path does not exist: {path}")
            return self._process_directory(path_obj)

    def _process_file(
        self, file_path: Path, relative_path: Path
    ) -> Optional[Dict[str, str]]:
        """Process a single file, using markitdown if enabled"""
        self.log_debug(f"Processing file: {file_path}")

        try:
            if self.config.use_markitdown:
                file_ext = os.path.splitext(str(file_path))[1].lower()
                if (
                    self.config.markitdown_extensions is not None
                    and file_ext in self.config.markitdown_extensions
                ):
                    try:
                        self.log_debug(f"Attempting to process with markitdown")
                        assert self.markitdown is not None
                        result = self.markitdown.convert(str(file_path))
                        self.log_debug("Successfully processed with markitdown")
                        return {
                            "path": str(relative_path),
                            "content": result.text_content,
                        }
                    except (FileConversionException, UnsupportedFormatException) as e:
                        self.log_debug(
                            f"MarkItDown couldn't process {file_path}: {str(e)}"
                        )
                    except Exception as e:
                        self.log_debug(
                            f"Error with MarkItDown processing {file_path}: {str(e)}"
                        )

            # Fall back to normal reading
            self.log_debug("Attempting normal file reading")
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                self.log_debug("Successfully read file normally")
                return {"path": str(relative_path), "content": content}
        except Exception as e:
            self.log_debug(f"Error processing file: {str(e)}")
            return None

    def write_split_files(self, files: List[Dict[str, str]], base_path: Path) -> None:
        """Write individual files for each processed document.

        Args:
            files: List of dictionaries containing file paths and contents
            base_path: Base path for creating the output directory structure
        """
        if not self.split_output_dir:
            return

        output_dir = Path(self.split_output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for file_info in files:
            # Generate a unique identifier
            file_uuid = str(uuid.uuid4())

            # Create output file path
            output_file = output_dir / f"{file_uuid}.txt"

            # Prepare content with metadata header
            content = (
                f"Original Path: {file_info['path']}\n"
                f"Base Directory: {base_path}\n"
                f"UUID: {file_uuid}\n"
                f"{'=' * 50}\n\n"
                f"{file_info['content']}"
            )

            # Write the file
            with open(output_file, "w", encoding="utf-8", errors="ignore") as f:
                f.write(content)

    def _process_directory(
        self, path: Path, original_path: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """Internal method to process a directory"""
        files: List[Dict[str, str]] = []

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

        # Write split files if output directory is specified
        if self.split_output_dir:
            self.write_split_files(files, path)

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
        summary = f"Path analyzed: {original_path or path}\n"
        summary += f"Files processed: {len(files)}\n"
        if self.config.target_dir:
            summary += f"Target directory: {self.config.target_dir}\n"
        if self.config.use_markitdown:
            summary += "Using MarkItDown for compatible files\n"
            if self.config.markitdown_extensions:
                summary += f"MarkItDown extensions: {', '.join(self.config.markitdown_extensions)}\n"
        if self.branch:
            summary += f"Git branch: {self.branch}\n"
        if self.split_output_dir:
            summary += f"Split files output directory: {self.split_output_dir}\n"

        return summary, tree, content
