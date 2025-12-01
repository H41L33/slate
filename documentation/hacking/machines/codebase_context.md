# Slate Codebase Context

## Core Data Structures

### Block Dictionary (AST)
Simplified representation of Markdown elements.
```json
[
  {"h1": "Title"},
  {"p": "Paragraph content"},
  {"ul": ["Item 1", {"p": "Item 2", "ul": ["Nested"]}]},
  {"code": {"text": "print('hi')", "lang": "python"}},
  {"image": {"src": "img.png", "alt": "Alt", "caption": "Cap"}}
]
```

## API Signatures

### `src/slate/parse.py`
```python
def parse_markdown_to_dicts(mdtext: str) -> list[dict[str, Any]]
```

### `src/slate/render.py`
```python
class HTMLRenderer:
    def render_blocks(self, blocks: list[dict], title: str=None, description: str=None, date: str=None, time: str=None, source_date: str=None) -> str

class CustomTokenRegistry:
    @classmethod
    def register(cls, token_name: str, handler: Callable[[re.Match], str])

class VariableRegistry:
    @classmethod
    def register(cls, name: str, handler: Callable[[Dict[str, Any]], str])

```

## Regex Patterns
- **Link**: `r'\[(?P<label>[^\]]+)\]\((?P<href>[^\)]+)\)'`
- **Custom Token**: `r'\[!(?P<token>[A-Z0-9-_]+)\]\s*\[(?P<label>[^\]]+)\]\((?P<href>[^\)]+)\)'`

## Metadata Format
Injected into HTML footer for smart updates.
```html
<!-- slate: {"source": "/abs/path/input.md", "template": "/abs/path/template.html"} -->
```

## Template Variables
Managed by `VariableRegistry`.
- `{{date}}` / `{{updated-date}}`: Build date.
- `{{time}}` / `{{updated-time}}`: Build time.
- `{{source-date}}`: Source file modification date.
- `{{content}}`: Rendered HTML content.

