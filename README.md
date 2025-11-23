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

`pipx install slate`

### Or, with pip:

`pip install slate`

## Usage

### Generate a static HTML page

slate input.md page.html -t "Page Title" -o output_dir -n index.html

- **input.md**: Input markdown.
- **page.html**: HTML template.
- **-t "Page Title"**: Title override, `slate` will use the first H1 as the title otherwise.
- **-o output_dir**: Output directory.
- **-n index.html**: Output filename.

See test.md for all supported content types.

Callouts, images with captions, tables, and codeblocks are rendered with modern CSS and accessibility in mind.

## Limitations

- Nested lists, nested blockquotes, and multi-line items are not fully supported

- Complex tables with nested or block content will be flattened

- Markdown extensions not in CommonMark spec may be ignored

- All unsupported features are documented in the example page.

## Why Slate?
`slate` was created since I found other SSGs (Static Site Generators) to be needlessly complicated for my usage. All I needed to do was take some Markdown, and create HTML with correct classes, divs, etc, based on a template and a CSS file.

Because of that, `slate` is not as feature-full as other SSGs, but it is stupid-simple to get started with, and far easier to customise.

My personal website [link](https://about.haileywelsh.me) is created with `slate`. You can view the GitHub repo of that website to get an idea of how to extend `slate`.

`slate` is designed to be used with a monolithic CSS file, and maps Markdown elements to defined CSS classes.

Feel free to fork, modify, etc.

# License

[LGPL v3](https://www.gnu.org/licenses/lgpl-3.0.html#license-text)
