# Readium

A Python tool to extract and analyze documentation from repositories and directories.

## Features

- Read documentation files from directories or repositories
- Filter by file extensions and directories
- Exclude binary files and large files
- Configurable exclude/include patterns
- Command line interface and Python API

## Installation

```bash
pip install readium
```

## Usage

Command line:
```bash
# Basic usage
readium /path/to/directory

# Specify target subdirectory
readium /path/to/directory -t docs/argus

# Save to file
readium /path/to/directory -o output.txt

# Customize file size limit (in bytes)
readium /path/to/directory -s 2097152  # 2MB limit
```

Python API:
```python
from readium import Readium, ReadConfig

# Configure reader
config = ReadConfig(
    max_file_size=1024*1024,  # 1MB
    target_dir='docs/argus'    # Optional target subdirectory
)

# Create reader
reader = Readium(config)

# Read documentation
summary, tree, content = reader.read_docs('/path/to/directory')
```