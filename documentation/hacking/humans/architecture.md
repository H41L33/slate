# Slate Architecture Guide

## Philosophy
Slate is designed to be a **KISS (Keep It Simple, Stupid)**, reliable static site generator. It avoids complex configuration files and plugin systems in favor of a straightforward, monolithic design. The goal is to convert Markdown to accessible HTML (and other formats) with minimal fuss.

## Data Flow
1. **Input**: A Markdown file is read.
2. **Parsing**: `markdown-it-py` tokenizes the text. `slate.parse` converts these tokens into a simplified list of "Block Dictionaries" (AST).
3. **Rendering**: A Renderer class (e.g., `HTMLRenderer`) iterates over the blocks and produces the final output string.
4. **Output**: The result is saved to a file.

## Key Modules

### `src/slate/main.py`
The entry point. It handles:
- **CLI Arguments**: `build` and `update` commands.
- **Smart Update**: Logic to read metadata from existing HTML files to determine source and template paths without user input.
- **Orchestration**: Calls parser and renderer functions.

### `src/slate/parse.py`
Responsible for converting raw Markdown into Slate's internal AST.
- **`parse_markdown_to_dicts(mdtext)`**: The main function. Returns a list of dicts like `{'h1': 'Title'}`, `{'p': 'Content'}`.
- **Callouts**: Handles custom `[!NOTE]` style blocks.

### `src/slate/render.py`
Contains the rendering logic.
- **`HTMLRenderer`**: Converts blocks to HTML. Handles templates and variable injection (`{{date}}`, `{{source-date}}`).
- **`GemtextRenderer` / `GopherRenderer`**: Alternative formats.
- **`CustomTokenRegistry`**: A system to register custom Markdown tokens (e.g., `[!MD-PAGE]`, `[!BUTTON]`) and their handlers.
- **`VariableRegistry`**: A centralized system for managing template variables (`{{date}}`, `{{source-date}}`, etc.).

### `src/slate/loader.py`
Simple utilities for reading files and loading Jinja2 templates.

## Extending Slate
To add a new custom token (e.g., `[!BUTTON]`):
1. Open `src/slate/render.py`.
2. Define a handler function that takes a regex match and returns a string.
3. Register it: `CustomTokenRegistry.register("BUTTON", my_handler)`.

To add a new variable (e.g., `{{my-var}}`):
1. Open `src/slate/render.py`.
2. Register it: `VariableRegistry.register("my-var", lambda context: "My Value")`.
