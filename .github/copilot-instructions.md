## Quick Context

This repository implements a small, focused Markdown → HTML static site tool called `slate`.
- Source is under `src/slate/` (package `slate`).
- CLI entrypoint: `src/slate/main.py` (script `slate` configured in `pyproject.toml`).
- Parsing: `src/slate/parser.py` — converts Markdown string into Block objects.
- Block model: `src/slate/blocks.py` — central Block subclasses (Heading, Paragraph, List, ListItem, CodeBlock, InlineCode, Blockquote, Callout, Figure, Table, HorizontalRule, Link).
- Rendering: `src/slate/renderer.py` — turns Block objects into HTML using Jinja2 templates.

## High-level Architecture (why/how)

- Single-process CLI: reads Markdown, parses into an intermediate Block AST, then renders HTML via Jinja2.
- Parser is intentionally conservative and custom — many tests and behavior rely on the specific Block types and shapes defined in `blocks.py`.
- Tests assert the structure of the AST (for example, `ListItem.content` may be either `str` or `list[Block]`; nested lists are attached via `ListItem.nested_list`). Change parser output carefully.

## Developer workflows & commands

- Use Poetry to run and test consistently (the project requires Python >= `3.14`):

```fish
poetry install
poetry run pytest -q
poetry run python -m src.slate.main --help   # or: poetry run slate
```

- Add development dependencies with Poetry (already uses a dev group for `pytest`):
```fish
poetry add --dev <package>
```

- Quick debug harness: `scripts/debug_parse.py` exists and can be run to exercise parser edge-cases:
```fish
poetry run python scripts/debug_parse.py
```

## Project-specific conventions & patterns (important for editing)

- Block types drive behavior — tests validate Block shapes, not just text output. When changing parser or blocks:
  - Keep `List`, `ListItem`, and `Paragraph` semantics stable.
  - `ListItem.content` may be a `str` (single-line content) or a `list[Block]` (multi-line or paragraph content inside an item).
  - Nested lists: parser attaches nested `List` to the parent `ListItem` via `ListItem.nested_list` instead of duplicating top-level list blocks.
- Parser responsibilities:
  - Recognize headings, fenced code blocks (```````), blockquotes, callouts (`[!NOTE]`-style), images, inline code (backticks), lists (ordered/unordered) with nesting and continuation lines, and paragraphs.
  - Render inline code to `InlineCode(...).render()` when inlining into list/inline text values (renderer expects that form in some tests).
- Tests define canonical behavior. When in doubt, open `tests/test_parser.py` and `tests/test_list_continuation.py` to see expected AST shapes.

## Files you will edit most often

- `src/slate/parser.py` — primary area for parsing fixes and features described in `Plan.md`.
- `src/slate/blocks.py` — definitions of AST nodes; change types carefully as tests rely on exact shapes.
- `src/slate/renderer.py` — HTML output; follow existing helpers and patterns.
- `src/slate/main.py` — CLI wiring for end-to-end runs.
- `tests/` — run tests frequently; they encode intended behavior.

## Integration points & external dependencies

- Uses `markdown-it-py` (plugins), `jinja2`, and `beautifulsoup4` (see `pyproject.toml`).
- The CLI is installed as a console script via Poetry; tests and scripts assume running inside the Poetry virtualenv.

## Tips for an AI code agent working here

- Small, focused changes: prefer minimal diffs to `parser.py`. Tests are specific; update tests only when intent changes across the project.
- Always run `poetry run pytest -q` after parsing or block-model changes. Many failures are structural (AST shape), not purely textual.
- When modifying `List`/`ListItem` behavior:
  - Search tests for `ListItem.content` expectations and replicate the shape (string vs list of `Paragraph` blocks).
  - Avoid appending nested lists as separate top-level blocks — attach them to the parent item.
- Use `scripts/debug_parse.py` to reproduce hard-to-isolate parsing cases before running full test suite.
- Keep `pyproject.toml`'s `requires-python` in mind: features requiring modern typing or syntax are acceptable.

## Examples (patterns observed in the codebase)

- To add a nested-list item, parser code sets `parent_item.nested_list = nested_list` rather than appending `nested_list` to the global `blocks` list.
- Paragraph accumulation: consecutive non-block lines are merged into a single `Paragraph` block and assigned to `ListItem.content` as `list[Paragraph]` when continuation lines occur.
- Inline code rendering: inside list text the parser calls `InlineCode(token).render()` and inserts that HTML string inside content strings.

## Where to look next / common pitfalls

- `tests/test_parser.py` and `tests/test_list_continuation.py` — canonical behavior for parser changes.
- `test.md` — collection of supported Markdown features used as a human-visible spec.
- Be careful with string quoting and indentation in parser regexes — earlier commits introduced syntax errors when editing large functions.

---

If anything here is unclear or you want sections extended (for example, a short developer checklist or a recommended PR template), tell me which parts to expand and I'll iterate.
