from dataclasses import dataclass, field
from typing import (  # Add Tuple and Union for function return type
    Literal,
    Optional,
    Set,
    Tuple,
    Union,
)

DEFAULT_EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    "assets",
    "img",
    "images",
    "dist",
    "build",
    ".next",
    ".vscode",
    ".idea",
    "bin",
    "obj",
    "target",
    "out",
    ".venv",
    "venv",
    ".gradle",
    ".pytest_cache",
    ".mypy_cache",
    "htmlcov",
    "coverage",
    ".vs",
    "Pods",
}

DEFAULT_EXCLUDE_FILES = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".DS_Store",
    ".gitignore",
    ".env",
    "Thumbs.db",
    "desktop.ini",
    "npm-debug.log",
    "yarn-error.log",
    "pnpm-debug.log",
    "*.log",
    "*.lock",
}

DEFAULT_INCLUDE_EXTENSIONS = {
    ".md",
    ".mdx",
    ".txt",
    ".yml",
    ".yaml",
    ".rst",
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".rs",
    ".go",
    ".rb",
    ".php",
    ".sh",
    ".swift",
    ".kt",
    ".kts",
    ".scala",
    ".pl",
    ".pm",
    ".r",
    ".jl",
    ".lua",
    ".dart",
    ".m",
    ".mm",
    ".cs",
    ".vb",
    ".fs",
    ".asm",
    ".s",
    ".v",
    ".sv",
    ".vhd",
    ".vhdl",
    ".clj",
    ".cljs",
    ".groovy",
    ".hs",
    ".erl",
    ".ex",
    ".exs",
    ".ml",
    ".mli",
    ".nim",
    ".pas",
    ".pp",
    ".sql",
    ".adb",
    ".ads",
    ".ada",
    ".d",
    ".cr",
    ".nim",
    ".rkt",
    ".scm",
    ".ss",
    ".tcl",
    ".tk",
    ".bat",
    ".cmd",
    ".ps1",
    ".psm1",
    ".psd1",
    ".bas",
    ".cls",
    ".frm",
    ".ctl",
    ".vbproj",
    ".csproj",
    ".fsproj",
    ".vcxproj",
    ".xcodeproj",
    ".xcworkspace",
    ".sln",
    ".makefile",
    ".mk",
    ".cmake",
    ".gradle",
    ".pom",
    ".build",
    ".proj",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".json",
    ".xml",
    ".ipynb",
}

MARKITDOWN_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".xls",
    ".pptx",
    ".html",
    ".htm",
    ".msg",
}

# Add a new constant for URL processing modes
URL_MODES = Literal["full", "clean"]


@dataclass
class ReadConfig:
    """Configuration for document reading

    Attributes
    ----------
    exclude_extensions : Set[str]
        File extensions to exclude from processing (takes precedence over include_extensions).
    """

    max_file_size: int = 5 * 1024 * 1024  # 5MB default
    exclude_dirs: Set[str] = field(default_factory=lambda: DEFAULT_EXCLUDE_DIRS.copy())
    exclude_files: Set[str] = field(
        default_factory=lambda: DEFAULT_EXCLUDE_FILES.copy()
    )
    include_extensions: Set[str] = field(
        default_factory=lambda: DEFAULT_INCLUDE_EXTENSIONS.copy()
    )
    exclude_extensions: Set[str] = field(default_factory=set)
    target_dir: Optional[str] = None
    use_markitdown: bool = False
    markitdown_extensions: Optional[Set[str]] = field(
        default_factory=lambda: MARKITDOWN_EXTENSIONS.copy()
    )
    debug: bool = False
    url_mode: URL_MODES = "clean"  # URL processing mode (new)
    include_comments: bool = False  # Include web page comments (new)
    include_tables: bool = True  # Include tables from web pages (new)
    include_images: bool = True  # Include image references (new)
    include_links: bool = True  # Include links (new)
    show_token_tree: bool = False  # Show token tree (new)
    # Only tiktoken
    token_calculation: Literal[
        "tiktoken"
    ] = "tiktoken"  # Token calculation mode (only tiktoken)


def convert_url_to_markdown(url: str, config: ReadConfig) -> Tuple[str, str]:
    """
    Convert a URL to Markdown using trafilatura.

    Parameters
    ----------
    url : str
        URL to convert.
    config : ReadConfig
        Configuration for processing.

    Returns
    -------
    Tuple[str, str]:
        Extracted title, content in Markdown format.
    """
    import trafilatura
    from trafilatura.settings import use_config

    try:
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

    except Exception as e:
        raise ValueError(f"Error converting URL to Markdown: {str(e)}")
