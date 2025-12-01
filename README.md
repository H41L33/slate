# Slate

> **KISS, reliable, and accessible.**

Slate is a lightweight Python CLI tool for converting Markdown to accessible static HTML pages, Gemtext, and Gophermaps. Designed for blogs, knowledge bases, and personal sites where simplicity is paramount.

## Features

- **Semantic HTML**: Converts Markdown to accessible HTML5 with semantic tags.
- **Multi-Format**: Outputs to HTML, Gemini (Gemtext), and Gopher.
- **Smart Updates**: intelligently updates existing files without needing to re-specify arguments.
- **Dynamic Links**: Automatically converts `[!MD-PAGE]` links to `.html` in the output, keeping your Markdown portable.
- **Customizable**: Integrates with Jinja2 templates and outputs CSS-ready classes.
- **Extensible**: Easily add custom Markdown tokens via a registry system.

## Quickstart

### Install via pipx (recommended)

```bash
pipx install slate-md
```

### Or, with pip:

```bash
pip install slate-md
```

## Usage

### Build a new page

```bash
slate build <input> <output> [flags]
```

- `input`: Input Markdown file path.
- `output`: Output file path (e.g., `pages/post.html`).
- `-f, --format`: Output format: `html` (default), `gemini`, or `gopher`.
- `-T, --template`: Jinja2 HTML template file (required for `html` output).
- `-t, --title`: Optional title override; otherwise the first H1 is used.
- `-d, --description`: Optional meta description for the template.

### Update an existing page

Slate remembers the source file and template used to generate an HTML file.

```bash
slate update <output_file>
```

- `output_file`: The existing HTML file to update.

You can still override the input or template if needed:
```bash
slate update output.html input.md -T new_template.html
```

### Dynamic Links

Slate supports "Dynamic Links" to keep your Markdown navigable on GitHub/Obsidian but working correctly on your site.

Use the `[!MD-PAGE]` token:
```markdown
Check out my [!MD-PAGE] [Latest Post](posts/latest.md)
```
Slate converts this to:
```html
Check out my <a href="posts/latest.html" class="content-link">Latest Post</a>
```

### Template Variables

Your Jinja2 templates have access to these variables:

- `{{ content }}`: The rendered HTML content.
- `{{ title }}`: The page title.
- `{{ description }}`: The page description.
- `{{ date }}` / `{{ updated-date }}`: Build date (DD/MM/YYYY).
- `{{ time }}` / `{{ updated-time }}`: Build time (HH:MM).
- `{{ source-date }}`: Modification date of the source Markdown file.

## Why Slate?

Slate was created because many SSGs are needlessly complicated for me. Slate is a tiny tool that does one thing well: converts Markdown into accessible HTML (and other formats) using a template.

- **No Config Files**: Everything is CLI arguments or embedded metadata.
- **Monolithic CSS**: Designed to be used with a single CSS file.
- **Hackable**: The codebase is small and easy to extend. See `documentation/hacking` for details.

## Documentation

- [Architecture Guide](documentation/hacking/humans/architecture.md)
- [Codebase Context](documentation/hacking/machines/codebase_context.md)

## License

[LGPL v3](https://www.gnu.org/licenses/lgpl-3.0.html#license-text)
