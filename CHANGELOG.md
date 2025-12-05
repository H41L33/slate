# Changelog

All notable changes to this project will be documented in this file.

## v0.2.7 - 2025-12-02

### Added
- **Renderer Feature Parity**: Gemtext and Gopher renderers now support link extraction and extension conversion.
- **Link Extraction**: Links in paragraphs are extracted and appended as Gemtext links or Gopher menu items.
- **Extension Conversion**: `.md` links are automatically converted to `.gmi` or `.txt` in output.
- **GFM Support**: Task Lists and Horizontal Rules support across all formats.
- **Freezing**: "Golden Master" snapshot tests to prevent regressions.
- **Security Hardening**: Added `bandit` security auditing, `defusedxml` for safe XML parsing, and enabled Jinja2 autoescape.
- **Unified CLI:**
  - Introduced `slate draft` for scaffolding new sites (replaces `new site`).
  - Unified `slate build` to handle both full sites and single pages (replaces `page`).
  - Added `slate rebuild` to instantly re-run the last command.
  - Added support for `format` in frontmatter.
- **CLI Polish**: Standardized `rich` error messages and added `--dry-run` option to `clean` command.

### Changed
- **Type Safety**: Enforced stricter `mypy` configuration (`check_untyped_defs = true`, `ignore_missing_imports = false`) and fixed all type errors.
- **Refactoring**: Simplified `parse.py` by extracting block handlers into single-responsibility functions.

## v0.2.0 - 2024-12-01

**Major Release:** Site Management System

Slate v0.2.0 transforms from a single-file transpiler to a complete site management system while maintaining its core philosophy of simplicity and hackability.

### Added

- **Frontmatter Support:** YAML frontmatter parsing with fields: `title`, `description`, `template`, `category`, `type`, `date`, `author`
- **Site Discovery:** Automatic site structure discovery from `index.md` with category-based organization
- **Navigation Generation:** Auto-generated header navigation and category-specific page lists
- **`slate rebuild` Command:** Batch processing to rebuild entire site with one command
- **RSS Feed Generation:** Automatic RSS 2.0 feed generation for blog categories (`feed.xml`)
- **Table of Contents:** `{{toc}}` variable for auto-generated TOC from headings
- **Footnotes Support:** Markdown footnote syntax with automatic rendering
- **Default Template:** Minimal, hackable HTML template with inline documentation (`templates/default.html`)
- **New Template Variables:** `{{nav_header}}`, `{{nav_category}}`, `{{category_name}}`, `{{breadcrumbs}}`, `{{toc}}`

### Changed

- Frontmatter takes precedence over CLI arguments when both are present
- Blog posts (` type: blog`) now require `date` and `title` fields for validation

### Documentation

- Created comprehensive documentation in `.agent/` for LLMs
- Created human-readable guides in `documentation/hacking/humans/`
- Updated README with site management examples
- Added PyYAML and types-PyYAML dependencies

## v0.1.6

- Added `{{version}}` variable.
- Removed `{{source-date}}` variable.

## [0.1.5] - 2025-12-01

### Added

- Hotfix: Refactored template variables to avoid confusion and ensure persistence.
- Added `{{creation_date}}` and `{{creation_time}}` which persist the original creation timestamp.
- Added `{{modify_date}}` and `{{modify_time}}` which reflect the last regeneration timestamp.
- Removed `{{date}}`, `{{time}}`, `{{updated-date}}`, `{{updated-time}}`.


## [0.1.4] - 2025-12-01

### Added

- New `update` command to refresh existing files with smart metadata detection.
- Support for nested Markdown lists in the parser.
- Gemtext (Gemini) and Gopher renderers with improved output formatting.
- New CLI flags: `-i/--input`, `-T/--template`, `-o/--output`, `-t/--title`, `-d/--description`, `-f/--format`.
- `scripts/debug_parse.py` (internal debug harness used during parser work).

### Changed

- Refactor: renderer moved to class-based renderers and improved list handling.
- Parser and renderer improvements to better preserve AST shapes expected by tests.
- Tests: added CLI argument tests and multi-format rendering checks.
- CI: added `ruff` lint step, `black --check`, and a non-blocking `mypy` step; ruff configuration added.

### Fixed

- Fixed several parsing edge-cases around list continuation and nested items.

### Notes

- `pyproject.toml` was updated to include development tooling (`ruff`, `mypy`). Black was considered but not included.
- Version was bumped to `0.1.4`.

For full details, consult the git history for the `main` branch.
