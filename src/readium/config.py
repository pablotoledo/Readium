from dataclasses import dataclass, field
from typing import Optional, Set

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


@dataclass
class ReadConfig:
    """Configuration for document reading"""

    max_file_size: int = 5 * 1024 * 1024  # 5MB default
    exclude_dirs: Set[str] = field(default_factory=lambda: DEFAULT_EXCLUDE_DIRS.copy())
    exclude_files: Set[str] = field(
        default_factory=lambda: DEFAULT_EXCLUDE_FILES.copy()
    )
    include_extensions: Set[str] = field(
        default_factory=lambda: DEFAULT_INCLUDE_EXTENSIONS.copy()
    )
    target_dir: Optional[str] = None
    use_markitdown: bool = False
    markitdown_extensions: Optional[Set[str]] = field(
        default_factory=lambda: MARKITDOWN_EXTENSIONS.copy()
    )
    debug: bool = False
