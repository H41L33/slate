# Slate: Codebase Map

## Repository Structure

```
slate/
├── .agent/                    # LLM context files
├── .github/workflows/         # CI/CD configuration
│   └── ci.yml                 # GitHub Actions workflow
├── documentation/
│   └── hacking/
│       ├── humans/            # Human-readable docs
│       └── machines/          # LLM-optimized docs
├── src/slate/                 # Main package
│   ├── __init__.py            # Package metadata
│   ├── loader.py              # File loading utilities
│   ├── main.py                # CLI entry point
│   ├── parse.py               # Markdown parser
│   └── render.py              # Output renderers
├── templates/                 # Example templates
├── tests/                     # Test suite
├── pyproject.toml             # Poetry configuration
├── README.md                  # User documentation
└── CHANGELOG.md               # Version history
```

## Module Breakdown

### `src/slate/main.py` (302 lines)
**Purpose**: CLI interface and command orchestration

**Key Functions**:
- `get_title(blocks, override)`: Extract/override document title
- `save_text(text, output_path)`: Write output to file
- `render_html(...)`: HTML rendering pipeline
- `render_gemtext(...)`: Gemtext rendering pipeline
- `render_gopher(...)`: Gopher rendering pipeline
- `handle_build(args, parser)`: Process `build` command
- `handle_update(args, parser)`: Process `update` command with smart metadata
- `main()`: argparse setup and command dispatch

**Dependencies**:
- `argparse`: CLI argument parsing
- `importlib.metadata`: Version retrieval
- `json`: Metadata serialization
- `re`: Metadata extraction
- `datetime`: Timestamp generation
- `pathlib.Path`: File operations
- Internal: `loader`, `parse`, `render`

**Data Flow**:
1. Parse CLI args
2. Load Markdown file
3. Parse to block dicts
4. Generate/retrieve metadata (dates, version)
5. Render via format-specific renderer
6. Inject metadata (HTML only)
7. Save output

### `src/slate/parse.py` (16117 bytes)
**Purpose**: Convert Markdown text to structured block dictionaries

**Key Functions**:
- `parse_markdown_to_dicts(md_text)`: Main parser entry point
- `_parse_table(lines)`: Table parsing
- `_parse_list(lines, indent, ordered)`: Recursive list parsing
- `_parse_code_block(lines)`: Fenced code block parsing
- `_parse_callout(line)`: Callout block detection

**Output Format**: `list[dict[str, Any]]`
- Each dict represents one block
- Keys: `h1-h6`, `p`, `ul`, `ol`, `code`, `table`, `image`, `blockquote`, `callout-{type}`

**Parsing Strategy**:
- Line-by-line state machine
- Lookahead for block boundaries
- Recursive for nested lists
- Regex for inline elements

### `src/slate/render.py` (36161 bytes)
**Purpose**: Convert block dicts to output formats

**Key Classes**:
- `VariableRegistry`: Template variable handlers
- `CustomTokenRegistry`: Custom Markdown token handlers
- `BaseRenderer`: Abstract base for all renderers
- `HTMLRenderer`: HTML output with semantic tags
- `GemtextRenderer`: Gemini protocol output
- `GopherRenderer`: Gophermap output

**Key Functions**:
- `render_inline_links(text)`: Process inline Markdown → HTML
- `_escape(value)`: HTML entity escaping
- `_img_replace(match)`: Image Markdown → `<figure>`
- `_link_replace(match)`: Link Markdown → `<a>`
- `_custom_token_replace(match)`: Token dispatcher

**Rendering Flow**:
1. `render_blocks()` called with parsed blocks
2. Set instance variables (title, dates, version)
3. Iterate blocks, dispatch to type-specific handlers
4. Apply variable substitution via `_apply_dt()`
5. Return formatted string

**HTML Class Conventions**:
- All elements: `content-{type}` (e.g., `content-paragraph`)
- Callouts: `callout callout-{type}`
- Tables: `content-table`
- Lists: `content-list`

### `src/slate/loader.py` (1390 bytes)
**Purpose**: File I/O abstraction

**Key Functions**:
- `load_markdown(filepath)`: Read Markdown file as UTF-8
- `load_template(filepath)`: Load Jinja2 template

**Error Handling**:
- FileNotFoundError: Clear user messages
- UTF-8 decoding errors: Reported with filename

### `src/slate/__init__.py` (52 bytes)
**Purpose**: Package metadata

**Exports**:
```python
__version__ = "0.1.6"
__all__ = ["main"]
```

## Test Structure

### Test Files
- `test_cli_args.py`: CLI argument validation
- `test_dynamic_links.py`: `[!MD-PAGE]` token behavior
- `test_features.py`: VariableRegistry, basic rendering
- `test_multi_format_outputs.py`: HTML/Gemtext/Gopher output
- `test_nested_lists.py`: Complex list structures
- `test_smart_update.py`: Metadata persistence
- `test_update_command.py`: `update` command integration

### Test Philosophy
- Mock file I/O where possible
- Real file operations in temp directories
- Integration tests for CLI commands
- Unit tests for parsers/renderers

## Data Flow Diagram

```
CLI Input
    ↓
argparse → handle_build/handle_update
    ↓
load_markdown(file) → Markdown string
    ↓
parse_markdown_to_dicts() → list[dict]
    ↓
get_title() → Extract/override title
    ↓
Generate timestamps + version
    ↓
Renderer.render_blocks() → Formatted string
    ↓
Template.render() → Final output (HTML only)
    ↓
Inject metadata (HTML only)
    ↓
save_text() → Write to disk
```

## Extension Points

### 1. Custom Tokens
```python
from slate.render import CustomTokenRegistry

def my_handler(match):
    return f'<custom>{match.group("label")}</custom>'

CustomTokenRegistry.register("MY-TOKEN", my_handler)
```

### 2. Template Variables
```python
from slate.render import VariableRegistry

VariableRegistry.register("my_var", lambda c: c.get("my_var", ""))
```

### 3. New Renderers
Subclass `BaseRenderer`, implement `render_blocks()`:
```python
class CustomRenderer(BaseRenderer):
    def render_blocks(self, blocks, **kwargs):
        super().render_blocks(blocks, **kwargs)
        # Custom rendering logic
        return formatted_string
```

## Configuration Files

### `pyproject.toml`
- Poetry dependencies
- Package metadata
- Pytest configuration
- Ruff/mypy settings

### `.github/workflows/ci.yml`
- Python 3.14 matrix
- Ruff linting
- Mypy type checking
- Pytest execution

## Import Graph

```
main.py
  ├→ loader.py
  ├→ parse.py
  └→ render.py
      └→ (no internal deps)
```

Clean dependency hierarchy, no circular imports.
