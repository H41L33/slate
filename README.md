# Slate

Slate is a KISS, reliable Python CLI tool for converting Markdown to accessible static HTML pages. Perfect for blogs, knowledge bases, and personal sites.

## Features

- Converts Markdown to HTML with semantic tags

- Supports headings, paragraphs, lists, tables, blockquotes, images, code blocks, inline code, and links

- Parses custom Markdown callouts (e.g., [!NOTE], [!WARNING])

- Integrates with Jinja2 templates for customizable page layout

-  Outputs HTML with CSS classes for instant theme support

- CLI usability: specify input, template, title override, and output destination

## Quickstart

bash

### Install via pipx (recommended)

`pipx install slate-md`

### Or, with pip:

`pip install slate-md`

## Usage

### Generate a static page (new CLI flags)

`slate -i input.md -T template.html -o out_dir -t "Page Title" -d "Short description" -f html`

- `-i, --input`: Input Markdown file path.
- `-T, --template`: Jinja2 HTML template file (required for `html` output).
- `-o, --output`: Output directory to write the rendered file(s).
- `-t, --title`: Optional title override; otherwise the first H1 is used.
- `-d, --description`: Optional meta description for the template.
- `-f, --format`: Output format: `html` (default), `gemini`, or `gopher`.

Examples:

- Render HTML: `slate -i mydoc.md -T page.html -o site -t "My Doc" -f html`
- Render Gemini (gemtext): `slate -i mydoc.md -o out -f gemini`
- Render Gopher: `slate -i mydoc.md -o out -f gopher`

See `test.md` for supported Markdown features and examples.

Callouts, images with captions, tables, and codeblocks are rendered with modern CSS and accessibility in mind.

## Limitations

- Nested lists, nested blockquotes, and multi-line items are not fully supported

- Complex tables with nested or block content will be flattened

- Markdown extensions not in CommonMark spec may be ignored

- All unsupported features are documented in the example page.

## Why Slate?

`slate` was created because many other SSGs were needlessly complicated for simple use cases. The goal was a tiny tool that converts Markdown into accessible HTML using a template and minimal configuration.

Because of that, `slate` is not as feature-full as other SSGs, but it is very simple to get started with and easier to customize.

My personal website, [Hailey's site](https://about.haileywelsh.me), is built with `slate`. You can view that repository for examples of how to extend `slate`.

`slate` is designed to be used with a monolithic CSS file, and maps Markdown elements to defined CSS classes.

Feel free to fork and modify.

## License

[LGPL v3](https://www.gnu.org/licenses/lgpl-3.0.html#license-text)
