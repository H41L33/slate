# Codebase Guide

This guide will walk you through Slate's codebase, explaining how everything fits together. Whether you're fixing a bug, adding a feature, or just exploring, this should help you navigate the code.

## Bird's Eye View

Slate has a simple, linear architecture:

```
Markdown File → Parser → Renderer → Output File
```

That's it! No complex build systems, no weird state management, no hidden magic. Let's break down each part.

## Directory Structure

```
slate/
├── src/slate/          # The actual code
│   ├── main.py         # CLI and command execution
│   ├── parse.py        # Markdown → structured data
│   ├── render.py       # Structured data → output
│   └── loader.py       # File I/O utilities
├── tests/              # Test suite
├── documentation/      # What you're reading now!
└── templates/          # Example templates
```

## The Code Modules

### `main.py`: The Entry Point

This is where everything starts. When you run `slate build` or `slate update`, you're calling functions in this file.

**Key functions**:

- `main()`: Sets up argparse,  handles CLI arguments
- `handle_build()`: Processes the `build` command
- `handle_update()`: Processes the `update` command with smart metadata reading
- `render_html/gemtext/gopher()`: Coordinate rendering for each format

**Flow**:
1. Parse command-line arguments
2. Load the Markdown file
3. Parse it into structured blocks
4. Get/generate metadata (title, dates, version)
5. Render to the specified format
6. Save the output

The "smart update" magic happens in `handle_update()`. It reads the HTML comment at the end of HTML files to figure out which Markdown file and template to use, so you don't have to specify them again.

### `parse.py`: Understanding Markdown

This module converts raw Markdown text into Python dictionaries. Each Markdown block (heading, paragraph, list, etc.) becomes a dict with specific keys.

**Example**:
```markdown
# Hello World
```

Becomes:
```python
{"h1": "Hello World"}
```

**How it works**:

The parser reads Markdown line by line, building up a list of block dictionaries. It handles:

- **Headings**: `# H1` through `###### H6`
- **Paragraphs**: Plain text
- **Lists**: Both ordered and unordered, including nested ones
- **Code blocks**: Fenced with triple backticks
- **Tables**: Pipe-separated values
- **Images**: `![alt](src "caption")`
- **Callouts**: `[!NOTE]` through `[!TIP]`

The trickiest part is **nested lists**. The parser uses recursion to handle lists within lists, tracking indentation levels to figure out the structure.

**Important function**: `parse_markdown_to_dicts(md_text)` is your starting point for any parsing questions.

### `render.py`: Making It Pretty

This is the biggest file in the project. It takes those structured dictionaries from the parser and converts them into HTML, Gemtext, or Gopher format.

**The Registry Pattern**:

Slate uses two registries to make things extensible:

1. **VariableRegistry**: Maps template variables like `{{date}}` to Python functions
2. **CustomTokenRegistry**: Maps custom tokens like `[!MD-PAGE]` to handler functions

This means you can add new variables or tokens without modifying core rendering logic.

**The Renderer Classes**:

All renderers inherit from `BaseRenderer`:

- `HTMLRenderer`: Produces semantic HTML5 with CSS classes
- `GemtextRenderer`: Produces Gemini protocol output
- `GopherRenderer`: Produces Gophermap-compliant text

Each renderer implements `render_blocks()`, which iterates through the parsed blocks and converts them to the target format.

**HTML Rendering**:

For HTML, inline elements (links, images, code) are processed separately using regex patterns. This happens in `render_inline_links()`, which:

1. Converts images to `<figure>` tags
2. Handles custom tokens
3. Converts links to `<a>` tags
4. Wraps inline code in `<code>` tags

**Variable Substitution**:

The `_apply_dt()` method in `BaseRenderer` is where template variables get replaced. It:

1. Builds a context dict with all available variables
2. Uses regex to find `{{variable}}` patterns
3. Looks up the variable in the registry
4. Replaces the pattern with the value

### `loader.py`: File Operations

This is the simplest module. It has two functions:

- `load_markdown()`: Reads a Markdown file as UTF-8
- `load_template()`: Loads a Jinja2 template

Both handle errors gracefully, giving useful error messages when files are missing or unreadable.

## Data Structures

Understanding the data structures will help you work with the code more effectively.

### Block Dictionary

The core unit of Slate's internal representation:

```python
# Heading
{"h1": "My Title"}

# Paragraph
{"p": "Some text with **bold** and `code`"}

# List
{"ul": [
    "Item 1",
    {"p": "Item 2", "ul": ["Nested item"]}
]}

# Code block
{"code": {"lang": "python", "text": "print('hello')"}}

# Table
{"table": {
    "headers": ["Col1", "Col2"],
    "rows": [["A", "B"], ["C", "D"]]
}}

# Image
{"image": {"src": "pic.jpg", "alt": "Description", "caption": "Optional"}}
```

### Metadata Format

HTML files store metadata in comments:

```html
<!-- slate: {"source": "/path/to/file.md", "template": "/path/to/template.html", "creation_date": "01/01/2024", "creation_time": "12:00"} -->
```

This lets `slate update` work without needing a database or configuration files.

## Adding Features

### Adding a New Template Variable

1. Open `render.py`
2. Register your variable in the default registrations:
   ```python
   VariableRegistry.register("my_var", lambda c: c.get("my_var", "default"))
   ```
3. Pass the value when calling `render_blocks()` in `main.py`
4. Add it to the context dict in `BaseRenderer._apply_dt()`

### Adding a New Custom Token

1. Write a handler function following this signature:
   ```python
   def my_token_handler(match: re.Match) -> str:
       label = match.group("label")
       href = match.group("href")
       return f'<custom>{label}</custom>'
   ```
2. Register it:
   ```python
   CustomTokenRegistry.register("MY-TOKEN", my_token_handler)
   ```
3. Use it in Markdown: `[!MY-TOKEN] [Label](href)`

### Adding a New Output Format

1. Create a new renderer class inheriting from `BaseRenderer`
2. Implement `render_blocks()` to handle all block types
3. Add a new `render_<format>()` function in `main.py`
4. Add the format to argparse choices
5. Add tests!

## Testing Strategy

Slate's tests are organized by feature:

- `test_cli_args.py`: Command-line argument validation
- `test_dynamic_links.py`: Dynamic link token behavior
- `test_features.py`: Core rendering features
- `test_multi_format_outputs.py`: HTML/Gemtext/Gopher output
- `test_nested_lists.py`: Complex list parsing
- `test_smart_update.py`: Metadata persistence
- `test_update_command.py`: Update command integration

Tests use temporary directories (via `tempfile`) for file I/O and mocks (via `unittest.mock`) to avoid hitting the filesystem when possible.

## Common Patterns

### Error Handling

Slate uses `argparse` error handling for user-facing errors:

```python
main_parser.error("Clear error message here")
```

This exits with code 1 and prints a helpful message.

### Path Handling

Always use `pathlib.Path` for file operations:

```python
from pathlib import Path

path = Path(args.input)
if not path.exists():
    # handle it
```

### Type Hints

All functions have type hints. Use `str | None` for optional strings, `list[dict[str, Any]]` for blocks.

## Debugging Tips

1. **Parser issues**: Add print statements in `parse_markdown_to_dicts()` to see the blocks being created
2. **Renderer issues**: Print the blocks before rendering to see if parsing is correct
3. **Variable issues**: Check `BaseRenderer._apply_dt()` to see what's in the context
4. **CLI issues**: Add `print(args)` in `handle_build/update()` to see what argparse parsed

## Next Steps

- Explore the code! Start with `main.py` and follow the flow
- Run the tests: `poetry run pytest -v` to see everything in action
- Check the [Development Setup](development_setup.md) to get your environment ready
- Read the [CI Workflow](ci_workflow.md) to understand our quality standards
