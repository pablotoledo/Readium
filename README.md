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

Readium CLI extrae documentación y estructura de archivos de directorios, repositorios Git o URLs.

### Ejemplo básico

```bash
$ readium docs/
```

Esto mostrará la tabla de tokens (token tree), el árbol de archivos y el resumen.

### Mostrar solo la tabla de tokens

```bash
$ readium --tokens docs/
# o
$ readium tokens docs/
```

### Otras opciones

- `--max-file-size <bytes>`: Tamaño máximo de archivo a procesar (por defecto 5MB)
- `--target-dir <dir>`: Subdirectorio objetivo para la extracción
- `--use-markitdown`: Habilita MarkItDown para conversión Markdown
- `--debug`: Muestra logs de depuración

### Notas
- El token tree siempre aparece por defecto en la salida estándar.
- No existe un flag para desactivar el token tree.

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

Readium siempre incluye una tabla de conteo de tokens (token tree) al inicio de la sección "tree" de la salida estándar, tanto en la CLI como en la API de Python. Esta tabla muestra el número de tokens por archivo y por directorio, utilizando el tokenizador tiktoken (compatible con modelos OpenAI).

### Ejemplo de salida estándar

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

### Mostrar solo la tabla de tokens

Para mostrar únicamente la tabla de tokens, use el flag `--tokens` o el subcomando `tokens`:

```bash
$ readium --tokens docs/
# o
$ readium tokens docs/
```

Esto funciona tanto con `readium` como con `python -m readium`.

### Notas
- El token tree siempre aparece por defecto en la salida estándar.
- No existe un flag para desactivar el token tree.
- El token tree utiliza tiktoken como único método de tokenización.

## 🔢 Token Tree (Conteo de tokens por archivo/directorio)

Readium puede generar una tabla de conteo de tokens por archivo y directorio, útil para estimar el tamaño de los datos para modelos de lenguaje o para análisis de documentación.

- El token tree muestra la estructura de carpetas/archivos junto con el número de tokens estimados por cada uno.
- Puede usarse tanto desde la línea de comandos como desde la API Python.
- El conteo de tokens usa siempre la librería [tiktoken](https://github.com/openai/tiktoken) de OpenAI, igual que los modelos GPT-3.5/4.

### Ejemplo de salida
```
Token Tree:
└── README.md (tokens: 120)
└── docs/guide.md (tokens: 340)
└── src/example.py (tokens: 210)
Total tokens: 670
```

### CLI: Uso de Token Tree

```bash
# Mostrar el token tree (siempre usando tiktoken)
readium /ruta/al/proyecto --token-tree

# Desactivar el token tree (por defecto)
readium /ruta/al/proyecto --no-token-tree
```

- `--token-tree` activa la tabla de tokens.
- El conteo de tokens es siempre exacto usando tiktoken (igual que OpenAI).

### Python API: Uso de Token Tree

```python
from readium import Readium, ReadConfig

config = ReadConfig(
    show_token_tree=True,                # Activa el token tree
    # token_calculation ya no es necesario, siempre es tiktoken
)
reader = Readium(config)
summary, tree, content = reader.read_docs("/ruta/al/proyecto")
# El token tree estará incluido en el summary y/o tree
```

#### Instalación de tiktoken

Para usar el conteo de tokens, instala la dependencia:

```bash
poetry install --with tokenizers
# o
pip install tiktoken
```

---

## 🔢 Token Tree como utilidad independiente

Readium permite ahora obtener únicamente el listado de tokens por archivo/directorio sin procesar el resto de la documentación, usando el subcomando CLI:

### CLI: Solo token tree

```bash
readium tokens <ruta> [opciones]
```

- Ejemplo básico:
  ```bash
  readium tokens .
  ```
- Excluir extensiones:
  ```bash
  readium tokens . --exclude-ext .md
  ```

Esto mostrará únicamente la tabla de tokens (usando el método tiktoken, igual que OpenAI), sin el resumen ni el contenido de los archivos.

### ¿Cómo se cuentan los tokens?

Readium usa siempre la librería [tiktoken](https://github.com/openai/tiktoken) de OpenAI para contar tokens, igual que los modelos GPT-3.5/4. Esto te da una estimación realista de cuántos tokens consumiría tu texto en la API de OpenAI.

### Python API

Para uso programático, sigue usando `Readium.generate_token_tree()` sobre la lista de archivos procesados si solo quieres el token tree.

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
