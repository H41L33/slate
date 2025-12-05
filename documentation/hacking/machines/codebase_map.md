# Codebase Map

## Source Code (`src/slate/`)

- `__init__.py`: Package initialization.
- `frontmatter.py`: Handling of YAML frontmatter extraction and validation.
- `loader.py`: Loading of Markdown files and templates.
- `main.py`: Entry point for the CLI, handling argument parsing and command dispatch.
- `navigation.py`: Logic for generating site navigation (breadcrumbs, menus).
- `parse.py`: Markdown parsing logic using `markdown-it-py`.
- `rebuild.py`: Logic for incremental rebuilds or watching for changes.
- `render.py`: Renderers for HTML, Gemtext, and Gopher.
- `rss.py`: RSS feed generation.
- `scaffold.py`: Logic for scaffolding new projects.
- `site.py`: Site structure discovery and representation (Page, Category, Site classes).
- `toc_footnotes.py`: Handling of Table of Contents and Footnotes.

## Tests (`tests/`)

- `test_blog_listing.py`: Tests for granular blog listing variables.
- `test_cli_args.py`: Tests for CLI argument parsing.
- `test_dynamic_links.py`: Tests for dynamic link resolution.
- `test_features.py`: Tests for specific Markdown features.
- `test_freeze.py`: Snapshot tests for rendering.
- `test_frontmatter.py`: Tests for frontmatter handling.
- `test_ipfs.py`: Tests for IPFS compatibility.
- `test_multi_format_outputs.py`: Tests for multi-format build output.
- `test_navigation.py`: Tests for navigation generation.
- `test_nested_lists.py`: Tests for nested list rendering.
- `test_rss.py`: Tests for RSS feed generation.
- `test_rss_freeze.py`: Snapshot tests for RSS feeds.
- `test_sanity.py`: Basic sanity tests.
- `test_site_discovery.py`: Tests for site structure discovery.
- `test_structure.py`: Tests for output structure.
- `test_tipping.py`: Tests for tipping feature.
- `tests/test_toc_scrolling.py`: Tests for TOC scrolling and heading IDs.
- `tests/test_inline_code_regression.py`: Regression test for inline code spacing.

## Root Directory

- `reproduce_table.py`: Script to reproduce table rendering issues.
- `pyproject.toml`: Project configuration and dependencies.
- `poetry.lock`: Locked dependencies.
