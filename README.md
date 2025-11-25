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
  - **Automatic .gitignore support** - respects .gitignore patterns by default
- 🌐 **Process webpages and URLs** to convert directly to Markdown
  - Extract main content from documentation websites
  - Convert HTML to well-formatted Markdown
  - Support for tables, links, and images in converted content
- 🔄 **Convert multiple document formats** to Markdown using MarkItDown integration
- 🎯 **Target specific subdirectories** for focused analysis

## 🔄 MarkItDown Integration

Readium can use [MarkItDown](https://github.com/microsoft/markitdown) to convert a wide range of document formats directly to Markdown, including:

- PDF (`.pdf`)
- Word (`.docx`)
- Excel (`.xlsx`, `.xls`)
- PowerPoint (`.pptx`)
- HTML (`.html`, `.htm`)
- Outlook messages (`.msg`)

To enable this feature, use the `--use-markitdown` option in the CLI or set `use_markitdown=True` in the Python API. MarkItDown will be used automatically for all compatible files.

**Note:** The `markitdown` Python package must be installed. It is included as a dependency, but you can install it manually with:
```bash
pip install markitdown
```

**Example CLI usage:**
```bash
readium /path/to/directory --use-markitdown
```

When enabled, the summary will indicate:
```
Using MarkItDown for compatible files
MarkItDown extensions: .pdf, .docx, .xlsx, .pptx, .html, .msg
```
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

Readium CLI extracts documentation and file structure from directories, Git repositories, or URLs.

#### Basic Usage

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

# Enable MarkItDown integration (for PDF, DOCX, etc.)
readium /path/to/directory --use-markitdown

# Focus on specific subdirectory
readium /path/to/directory --target-dir docs/

# Disable .gitignore (process all files, including ignored ones)
readium /path/to/directory --no-gitignore
```

#### Advanced Options

```bash
# Customize file size limit (e.g., 10MB)
readium /path/to/directory --max-size 10485760

# Add custom directories to exclude (can be specified multiple times)
readium /path/to/directory --exclude-dir build --exclude-dir temp
# Or using the short form -x (can be repeated)
readium /path/to/directory -x build -x temp

# Include additional file extensions
readium /path/to/directory --include-ext .cfg --include-ext .conf

# Exclude specific file extensions (can be specified multiple times)
readium /path/to/directory --exclude-ext .json --exclude-ext .yml

# Enable debug mode for detailed processing information
readium /path/to/directory --debug

# Generate split files for fine-tuning
readium /path/to/directory --split-output ./training-data/

# Show only the token tree
readium --tokens /path/to/directory
# or
readium tokens /path/to/directory

# Process URL with content preservation mode
readium https://example.com/docs --url-mode full

# Process URL with main content extraction (default)
readium https://example.com/docs --url-mode clean

# Process directory and ignore .gitignore patterns
readium /path/to/directory --no-gitignore
```

#### Available Options

- `-o, --output <file>`: Save output to a specified file
- `-t, --target-dir <dir>`: Target subdirectory for extraction
- `-b, --branch <name>`: Specific Git branch to clone (only for Git repositories)
- `-s, --max-size <bytes>`: Maximum file size to process (default: 5MB)
- `-x, --exclude-dir <dir>`: Additional directories to exclude (can be specified multiple times)
- `-i, --include-ext <ext>`: Additional file extensions to include (can be specified multiple times)
- `-e, --exclude-ext <ext>`: File extensions to exclude (can be specified multiple times)
- `--split-output <dir>`: Directory for split output files (each file gets its own UUID-named file)
- `--url-mode <mode>`: URL processing mode: 'full' preserves all content, 'clean' extracts main content only (default: clean)
- `--use-markitdown/--no-markitdown`: Enable/disable MarkItDown for Markdown conversion of PDF, DOCX, etc.
- `--no-gitignore`: Disable .gitignore support (process all files, even those in .gitignore)
- `--debug/-d, --no-debug/-D`: Enable/disable debug mode
- `--tokens/--no-tokens`: Show/hide detailed token tree with file and directory token counts

#### Notes

- The default output includes summary, tree, and content.
- When using `--tokens` or the `tokens` subcommand, only the token tree is displayed.
- Do not use empty values with `-x`/`--exclude-dir`. Each value must be a valid directory name.
- The CLI will display the final list of excluded directories before processing.
- Default excluded directories include: `.git`, `node_modules`, `__pycache__`, etc.
- Default included file extensions cover most text and code files (`.md`, `.py`, `.js`, etc.).
- With MarkItDown integration, additional file types can be processed (`.pdf`, `.docx`, etc.).
- **By default, Readium respects `.gitignore` files** - use `--no-gitignore` to process all files.

### Python API

```python
from readium import Readium, ReadConfig

# Configure the reader
config = ReadConfig(
    max_file_size=5 * 1024 * 1024,  # 5MB limit
    target_dir='docs',               # Optional target subdirectory
    use_markitdown=True,            # Enable MarkItDown integration
    debug=True,                      # Enable debug logging
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
    debug=False,

    # Mostrar tabla de tokens por archivo/directorio
    show_token_tree=False,  # True para activar el token tree

    # Respect .gitignore patterns (default: True)
    use_gitignore=True,  # Set to False to process all files
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

2. **Tree**: Token table + file tree
   ```
   # Directory Token Tree
   | Directory | Files | Token Count |
   |-----------|-------|------------|
   | **.**     | 2     | 460        |
   | **docs**  | 1     | 340        |
   | **src**   | 1     | 210        |
   | └─ README.md |   | 120        |
   | └─ guide.md  |   | 340        |
   | └─ example.py|   | 210        |

   **Total Files:** 4
   **Total Tokens:** 670

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

> **Note:** The token tree (token count table) is now always included at the top of the 'tree' output, both in CLI and Python API, for all standard runs. The `--tokens` flag still works to show only the token tree if desired.

## 🔢 Token Tree (Token Counts)

Readium always includes a token count table (token tree) at the beginning of the "tree" section of the standard output, both in the CLI and the Python API. This table shows the number of tokens per file and per directory, using the tiktoken tokenizer (compatible with OpenAI models).

### Example of standard output

```bash
$ readium docs/

Token Tree:
| Path         | Tokens |
|-------------|--------|
| docs/       | 12345  |
| docs/a.md   | 2345   |
| docs/b.md   | 3456   |
| docs/sub/   | 4567   |
| docs/sub/x.py | 456   |

Tree:
- docs/
  - a.md
  - b.md
  - sub/
    - x.py

Summary:
- ...
```

### Show only the token tree

To show only the token tree, use the `--tokens` flag or the `tokens` subcommand:

```bash
$ readium --tokens docs/
# or
$ readium tokens docs/
```

This works with both `readium` and `python -m readium`.

### Notes
- The token tree always appears by default in the standard output.
- There is no flag to disable the token tree.
- The token tree uses tiktoken as the only tokenization method.

## 🔢 Token Tree (File/Directory Token Count)

Readium can generate a token count table by file and directory, useful for estimating data size for language models or for documentation analysis.

- The token tree displays the folder/file structure along with the estimated number of tokens for each.
- It can be used both from the command line and from the Python API.
- The token count always uses the [tiktoken](https://github.com/openai/tiktoken) library from OpenAI, just like the GPT-3.5/4 models.

### Example of output
```
Token Tree:
└── README.md (tokens: 120)
└── docs/guide.md (tokens: 340)
└── src/example.py (tokens: 210)
Total tokens: 670
```

### CLI: Using Token Tree

```bash
# Show the token tree (always using tiktoken)
readium /path/to/project --token-tree

# Disable the token tree (default)
readium /path/to/project --no-token-tree
```

- `--token-tree` activates the token table.
- Token counting is always accurate using tiktoken (same as OpenAI).

### Python API: Using Token Tree

```python
from readium import Readium, ReadConfig

config = ReadConfig(
    show_token_tree=True,                # Activate token tree
    # token_calculation is no longer needed, it's always tiktoken
)
reader = Readium(config)
summary, tree, content = reader.read_docs("/path/to/project")
# The token tree will be included in the summary and/or tree
```

#### Installing tiktoken

To use token counting, install the dependency:

```bash
poetry install --with tokenizers
# or
pip install tiktoken
```

---

## 🔢 Token Tree as an independent utility

Readium now allows you to get only the token list by file/directory without processing the rest of the documentation, using the CLI subcommand:

### CLI: Token tree only

```bash
readium tokens <path> [options]
```

- Basic example:
  ```bash
  readium tokens .
  ```
- Exclude extensions:
  ```bash
  readium tokens . --exclude-ext .md
  ```

This will show only the token table (using the tiktoken method, same as OpenAI), without the summary or file contents.

### How are tokens counted?

Readium always uses the [tiktoken](https://github.com/openai/tiktoken) library from OpenAI to count tokens, just like the GPT-3.5/4 models. This gives you a realistic estimate of how many tokens your text would consume in the OpenAI API.

### Python API

For programmatic use, continue using `Readium.generate_token_tree()` on the list of processed files if you only want the token tree.

---

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
