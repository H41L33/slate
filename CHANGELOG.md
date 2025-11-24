# Changelog

All notable changes to this project will be documented in this file.

## [0.1.4] - 2025-11-24

### Added

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
