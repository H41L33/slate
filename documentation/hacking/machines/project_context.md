# Slate: Project Context

## Identity
**Name**: Slate  
**Type**: Static Site Generator (SSG) / Markdown Compiler  
**License**: LGPL v3  
**Language**: Python 3.14+  
**Package**: `slate-md` (PyPI)

## Core Principles
1. **KISS (Keep It Simple, Stupid)**: Minimal complexity, maximum clarity
2. **Accessibility**: Semantic HTML5, proper ARIA attributes
3. **Reliability**: Stable, predictable behavior
4. **No configuration files**: Everything via CLI or embedded metadata
5. **Format agnostic**: HTML, Gemtext, Gopher from single source

## Primary Purpose
Convert Markdown documents into accessible static output formats (HTML, Gemini, Gopher) using Jinja2 templates, with smart update capabilities and dynamic link transformation.

## Target Use Cases
- Personal blogs
- Knowledge bases
- Documentation sites
- Small-to-medium static websites
- Alternative protocol content (Gemini/Gopher)

## Current Features (v0.1.6)

### Core Functionality
- **Multi-format output**: HTML, Gemtext (.gmi), Gopher (.txt)
- **Jinja2 templating**: Custom HTML templates with variable injection
- **Smart updates**: Re-render files without re-specifying arguments (metadata persistence)
- **Dynamic links**: `[!MD-PAGE]` token converts `.md` → `.html` links
- **Custom tokens**: Extensible token registry (e.g., `[!BUTTON]`)

### Markdown Support
- Headings (h1-h6)
- Paragraphs, blockquotes
- Unordered/ordered lists (nested)
- Code blocks with syntax highlighting support
- Images with captions
- Tables
- Inline code, links, images
- Callouts: `[!NOTE]`, `[!WARNING]`, `[!DANGER]`, `[!SUCCESS]`, `[!TIP]`

### Template Variables
- `{{content}}`: Rendered content
- `{{title}}`: Page title (from first h1/h2 or CLI override)
- `{{description}}`: Meta description
- `{{creation_date}}`: Original creation date (persistent)
- `{{creation_time}}`: Original creation time (persistent)
- `{{modify_date}}`: Last regeneration date
- `{{modify_time}}`: Last regeneration time
- `{{version}}`: Slate version

### CLI Commands
- `slate build <input> <output>`: Generate new file
- `slate update <output>`: Regenerate from embedded metadata

## Architecture Philosophy
- **Block-oriented parsing**: Markdown → structured dicts → renderers
- **Renderer pattern**: Separate renderers for HTML/Gemtext/Gopher
- **Registry systems**: CustomTokenRegistry, VariableRegistry for extensibility
- **Metadata injection**: HTML comments store source/template paths

## Anti-Patterns (What Slate Avoids)
- ❌ Complex configuration files (YAML/TOML/JSON)
- ❌ Plugin systems requiring installation
- ❌ Build directories with complex folder structures
- ❌ Asset pipelines (CSS/JS bundling)
- ❌ Development servers with hot reload
- ❌ Theme marketplaces

## Design Constraints
- Single CSS file assumption (monolithic styling)
- No JavaScript processing
- No asset optimization
- No content organization (user manages structure)
- Simple metadata (JSON in HTML comments only)

## Quality Standards
- Type hints required (mypy strict)
- 100% test coverage goal
- Ruff linting compliance
- Pytest for all features
- CI checks before merge to main
