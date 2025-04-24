# 📚 Readium

A powerful Python tool for extracting, analyzing, and converting documentation from repositories, directories, and URLs into accessible formats.

<p align="center">
  <img src="logo.webp" alt="Readium" width="80%">
</p>

## ✨ Features

- 📂 **Extract documentation** from local directories or Git repositories
  - Support for private repositories using tokens
  - Branch selection for Git repositories
  - Secure token handling and masking
- 🌐 **Process webpages and URLs** to convert directly to Markdown
  - Extract main content from documentation websites
  - Convert HTML to well-formatted Markdown
  - Support for tables, links, and images in converted content
- 🔄 **Convert multiple document formats** to Markdown using MarkItDown integration
- 🎯 **Target specific subdirectories** for focused analysis
- ⚡ **Process a wide range of file types**:
  - Documentation files (`.md`, `.mdx`, `.rst`, `.txt`)
  - Code files (`.py`, `.js`, `.java`, etc.)
  - Configuration files (`.yml`, `.toml`, `.json`, etc.)
  - Office documents with MarkItDown (`.pdf`, `.docx`, `.xlsx`, `.pptx`)
  - Webpages and HTML via direct URL processing
- 🎛️ **Highly configurable**:
  - Customizable file size limits
  - Flexible file extension filtering
  - Directory exclusion patterns
  - Binary file detection
  - Debug mode for detailed processing information
- 🔍 **Advanced error handling and debugging**:
  - Detailed debug logging
  - Graceful handling of unprintable content
  - Robust error reporting with Rich console support
- 📝 **Split output for fine-tuning** language models

## 🚀 Installation

```bash
# Using pip
pip install readium

# Using poetry
poetry add readium
```

## 📋 Usage

### Command Line Interface

**Basic usage:**
```bash
# Process a local directory
readium /path/to/directory

# Process a public Git repository
readium https://github.com/username/repository

# Process a specific branch of a Git repository
readium https://github.com/username/repository -b feature-branch

# Process a private Git repository with token
readium https://token@github.com/username/repository

# Process a webpage and convert to Markdown
readium https://example.com/documentation

# Save output to a file
readium /path/to/directory -o output.md

# Enable MarkItDown integration
readium /path/to/directory --use-markitdown

# Focus on specific subdirectory
readium /path/to/directory --target-dir docs/
```

**Advanced options:**
```bash
# Customize file size limit (e.g., 10MB)
readium /path/to/directory --max-size 10485760

# Add custom directories to exclude
readium /path/to/directory --exclude-dir build --exclude-dir temp

# Include additional file extensions
readium /path/to/directory --include-ext .cfg --include-ext .conf

# Exclude specific file extensions (can be specified multiple times)
readium /path/to/directory --exclude-ext .json --exclude-ext .yml

# Enable debug mode for detailed processing information
readium /path/to/directory --debug

# Generate split files for fine-tuning
readium /path/to/directory --split-output ./training-data/

# Process URL with content preservation mode
readium https://example.com/docs --url-mode full

# Process URL with main content extraction (default)
readium https://example.com/docs --url-mode clean
```

### Python API

```python
from readium import Readium, ReadConfig

# Configure the reader
config = ReadConfig(
    max_file_size=5 * 1024 * 1024,  # 5MB limit
    target_dir='docs',               # Optional target subdirectory
    use_markitdown=True,            # Enable MarkItDown integration
    debug=True                      # Enable debug logging
)

# Initialize reader
reader = Readium(config)

# Process directory
summary, tree, content = reader.read_docs('/path/to/directory')

# Process public Git repository
summary, tree, content = reader.read_docs('https://github.com/username/repo')

# Process specific branch of a Git repository
summary, tree, content = reader.read_docs(
    'https://github.com/username/repo',
    branch='feature-branch'
)

# Process private Git repository with token
summary, tree, content = reader.read_docs('https://token@github.com/username/repo')

# Process a webpage and convert to Markdown
summary, tree, content = reader.read_docs('https://example.com/documentation')

# Access results
print("Summary:", summary)
print("\nFile Tree:", tree)
print("\nContent:", content)
```

## 🌐 URL to Markdown

Readium can process web pages and convert them directly to Markdown:

```bash
# Process a webpage
readium https://example.com/documentation

# Save the output to a file
readium https://example.com/documentation -o docs.md

# Process URL preserving more content
readium https://example.com/documentation --url-mode full

# Process URL extracting only main content (default)
readium https://example.com/documentation --url-mode clean
```

### URL Conversion Configuration

The URL to Markdown conversion can be configured with several options:

- `--url-mode`: Processing mode (`clean` or `full`)
  - `clean` (default): Extracts only the main content, ignoring menus, ads, etc.
  - `full`: Attempts to preserve most of the page content

### Python API for URLs

```python
from readium import Readium, ReadConfig

# Configure with URL options
config = ReadConfig(
    url_mode="clean",  # 'clean' or 'full'
    include_tables=True,
    include_images=True,
    include_links=True,
    include_comments=False,
    debug=True
)

reader = Readium(config)

# Process a URL
summary, tree, content = reader.read_docs('https://example.com/documentation')

# Save the content
with open('documentation.md', 'w', encoding='utf-8') as f:
    f.write(content)
```

Readium uses [trafilatura](https://github.com/adbar/trafilatura) for web content extraction and conversion, which is especially effective for extracting the main content from technical documentation, tutorials, and other web resources.

## 🔧 Configuration

The `ReadConfig` class supports the following options:

```python
config = ReadConfig(
    # File size limit in bytes (default: 5MB)
    max_file_size=5 * 1024 * 1024,

    # Directories to exclude (extends default set)
    exclude_dirs={'custom_exclude', 'temp'},

    # Files to exclude (extends default set)
    exclude_files={'.custom_exclude', '*.tmp'},

    # File extensions to include (extends default set)
    include_extensions={'.custom', '.special'},

    # File extensions to exclude (takes precedence over include_extensions)
    exclude_extensions={'.json', '.yml'},

    # Target specific subdirectory
    target_dir='docs',

    # Enable MarkItDown integration
    use_markitdown=True,

    # Specify extensions for MarkItDown processing
    markitdown_extensions={'.pdf', '.docx', '.xlsx'},

    # URL processing mode: 'clean' or 'full'
    url_mode='clean',

    # URL content options
    include_tables=True,
    include_images=True,
    include_links=True,
    include_comments=False,

    # Enable debug mode
    debug=False
)
```

### Default Configuration

#### Default Excluded Directories
```python
DEFAULT_EXCLUDE_DIRS = {
    ".git", "node_modules", "__pycache__", "assets",
    "img", "images", "dist", "build", ".next",
    ".vscode", ".idea", "bin", "obj", "target",
    "out", ".venv", "venv", ".gradle",
    ".pytest_cache", ".mypy_cache", "htmlcov",
    "coverage", ".vs", "Pods"
}
```

#### Default Excluded Files
```python
DEFAULT_EXCLUDE_FILES = {
    ".pyc", ".pyo", ".pyd", ".DS_Store",
    ".gitignore", ".env", "Thumbs.db",
    "desktop.ini", "npm-debug.log",
    "yarn-error.log", "pnpm-debug.log",
    "*.log", "*.lock"
}
```

#### Default Included Extensions
```python
DEFAULT_INCLUDE_EXTENSIONS = {
    ".md", ".mdx", ".txt", ".yml", ".yaml", ".rst",
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java",
    # (Many more included - see config.py for complete list)
}
```

**Note:** If a file extension is specified in both `include_extensions` and `exclude_extensions`, the exclusion takes precedence and files with that extension will not be processed.

#### Default MarkItDown Extensions
```python
MARKITDOWN_EXTENSIONS = {
    ".pdf", ".docx", ".xlsx", ".xls",
    ".pptx", ".html", ".htm", ".msg"
}
```

## 📜 Output Format

Readium generates three types of output:

1. **Summary**: Overview of the processing results
   ```
   Path analyzed: /path/to/directory
   Files processed: 42
   Target directory: docs
   Using MarkItDown for compatible files
   MarkItDown extensions: .pdf, .docx, .xlsx, ...
   ```

2. **Tree**: Visual representation of processed files
   ```
   Documentation Structure:
   └── README.md
   └── docs/guide.md
   └── src/example.py
   ```

3. **Content**: Full content of processed files
   ```
   ================================================
   File: README.md
   ================================================
   [File content here]

   ================================================
   File: docs/guide.md
   ================================================
   [File content here]
   ```

## 📝 Split Output for Fine-tuning

When using the `--split-output` option or setting `split_output_dir` in the Python API, Readium will generate individual files for each processed document. This is particularly useful for creating datasets for fine-tuning language models.

Each output file:
- Has a unique UUID-based name (e.g., `123e4567-e89b-12d3-a456-426614174000.txt`)
- Contains metadata headers with:
  - Original file path
  - Base directory
  - UUID
- Includes the complete original content
- Is saved with UTF-8 encoding

Example output file structure:
```
Original Path: src/documentation/guide.md
Base Directory: /path/to/repository
UUID: 123e4567-e89b-12d3-a456-426614174000
==================================================

[Original file content follows here]
```

### Usage Examples

Command Line:
```bash
# Basic split output
readium /path/to/repository --split-output ./training-data/

# Combined with other features
readium /path/to/repository \
    --split-output ./training-data/ \
    --target-dir docs \
    --use-markitdown \
    --debug

# Process a URL and create split files
readium https://example.com/docs \
    --split-output ./training-data/ \
    --url-mode clean
```

Python API:
```python
from readium import Readium, ReadConfig

# Configure with all relevant options
config = ReadConfig(
    target_dir='docs',
    use_markitdown=True,
    debug=True
)

reader = Readium(config)
reader.split_output_dir = "./training-data/"

# Process and generate split files
summary, tree, content = reader.read_docs('/path/to/repository')

# Process a URL and generate split files
summary, tree, content = reader.read_docs('https://example.com/docs')
```

## 🛠️ Development

1. Clone the repository
   ```bash
   git clone https://github.com/pablotoledo/readium.git
   cd readium
   ```

2. Install development dependencies:
   ```bash
   # Using pip
   pip install -e ".[dev]"

   # Or using Poetry
   poetry install --with dev
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run tests without warnings
pytest -p no:warnings

# Run tests for specific Python version
poetry run pytest
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Microsoft and MarkItDown for their powerful document conversion tool
- Trafilatura for excellent web content extraction capabilities
- Rich library for beautiful console output
- Click for the powerful CLI interface
