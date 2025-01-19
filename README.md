# 📚 Readium

A powerful Python tool for extracting, analyzing, and converting documentation from repositories and directories into accessible formats.

<p align="center">
  <img src="logo.webp" alt="Readium" width="80%">
</p>

## ✨ Features

- 📂 Extract documentation from local directories or Git repositories
  - Support for private repositories using tokens
  - Branch selection for Git repositories
  - Secure token handling and masking
- 🔄 Convert multiple document formats to Markdown using MarkItDown integration
- 🎯 Target specific subdirectories for focused analysis
- ⚡ Process a wide range of file types:
  - Documentation files (`.md`, `.mdx`, `.rst`, `.txt`)
  - Code files (`.py`, `.js`, `.java`, etc.)
  - Configuration files (`.yml`, `.toml`, `.json`, etc.)
  - Office documents with MarkItDown (`.pdf`, `.docx`, `.xlsx`, `.pptx`)
- 🎛️ Highly configurable:
  - Customizable file size limits
  - Flexible file extension filtering
  - Directory exclusion patterns
  - Binary file detection
  - Debug mode for detailed processing information
- 🔍 Advanced error handling and debugging:
  - Detailed debug logging
  - Graceful handling of unprintable content
  - Robust error reporting with Rich console support

## 🚀 Installation

```bash
pip install readium

# Or with poetry
poetry add readium
```

## 📋 Usage

### Command Line Interface

Basic usage:
```bash
# Process a local directory
readium /path/to/directory

# Process a public Git repository
readium https://github.com/username/repository

# Process a specific branch of a Git repository
readium https://github.com/username/repository -b feature-branch

# Process a private Git repository with token
readium https://token@github.com/username/repository

# Process a specific branch of a private repository
readium https://token@github.com/username/repository -b feature-branch

# Save output to a file
readium /path/to/directory -o output.md

# Enable MarkItDown integration
readium /path/to/directory --use-markitdown

# Focus on specific subdirectory
readium /path/to/directory --target-dir docs/
```

Advanced options:
```bash
# Customize file size limit (e.g., 10MB)
readium /path/to/directory --max-size 10485760

# Add custom directories to exclude
readium /path/to/directory --exclude-dir build --exclude-dir temp

# Include additional file extensions
readium /path/to/directory --include-ext .cfg --include-ext .conf

# Enable debug mode for detailed processing information
readium /path/to/directory --debug

# Process specific branch with debug information
readium https://github.com/username/repository -b develop --debug
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

# Process specific branch of a private repository
summary, tree, content = reader.read_docs(
    'https://token@github.com/username/repo',
    branch='feature-branch'
)

# Access results
print("Summary:", summary)
print("\nFile Tree:", tree)
print("\nContent:", content)
```

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

    # Target specific subdirectory
    target_dir='docs',

    # Enable MarkItDown integration
    use_markitdown=True,

    # Specify extensions for MarkItDown processing
    markitdown_extensions={'.pdf', '.docx', '.xlsx'},

    # Enable debug mode
    debug=False
)
```

[Rest of the README content remains unchanged...]