# Reference Slate Site

This document outlines the structure of a standard Slate site and provides minimal reference templates for supported formats.

## Directory Structure

A typical Slate site (created via `slate draft my-site`) looks like this:

```text
my-site/
├── content/
│   ├── index.md            # Homepage
│   └── blog/
│       ├── blog.md         # Blog index
│       └── hello-world.md  # Blog post
├── templates/
│   └── base.html           # HTML Jinja2 template
├── static/
│   └── style.css           # CSS stylesheet
└── slate.json              # Build state (auto-generated)
```

## Reference Templates

### 1. Markdown Content (`content/index.md`)

Slate uses Markdown with YAML frontmatter. This is the source for **all** output formats (HTML, Gemini, Gopher).

```markdown
---
title: Welcome to Slate
template: base.html
categories: [blog]
---

# Welcome to Slate

Slate is a static site generator designed for simplicity.

## Features
- **Bold**, *Italic*, ~~Strikethrough~~
- [Links](https://example.com)
- Lists
    - Item 1
    - Item 2

> [!NOTE]
> This is a callout.
```

### 2. HTML Template (`templates/base.html`)

Slate uses **Jinja2** for HTML templating.

**Variables Available:**
- `{{ title }}`: Page title.
- `{{ content }}`: Rendered HTML content.
- `{{ nav_header }}`: Generated navigation links.
- `{{ version }}`: Slate version.
- `{{ creation_date }}`, `{{ modify_date }}`: Dates.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="static/style.css">
</head>
<body>
    <header>
        <nav>
            {{ nav_header }}
        </nav>
    </header>

    <main>
        {{ content }}
    </main>

    <footer>
        <p>Powered by Slate {{ version }}</p>
    </footer>
</body>
</html>
```

### 3. CSS (`static/style.css`)

A minimal CSS file to style the HTML output.

```css
body {
    font-family: system-ui, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    line-height: 1.6;
}

header nav ul {
    list-style: none;
    padding: 0;
    display: flex;
    gap: 1rem;
}

a { color: #007bff; text-decoration: none; }
a:hover { text-decoration: underline; }

blockquote {
    border-left: 4px solid #ccc;
    margin: 0;
    padding-left: 1rem;
}
```

**Note:** Slate does not take any responsibility for the CSS, that is completely your domain. There are no plans, no intentions nor wants to introduce CSS processing into Slate.

### 4. Gemini & Gopher

**Note:** Gemini and Gopher formats do **not** use external templates like HTML. Slate automatically converts the Markdown content into Gemtext (`.gmi`) and Gophermap (`.txt`) following protocol standards.

To ensure good output for these formats:
- Use standard Markdown headings (`#`, `##`).
- Use standard lists (`-`, `1.`).
- Avoid complex HTML-only features (raw HTML tags).
- Links will be automatically formatted as `=> URL Label` in Gemtext and appropriate selectors in Gopher.

**Example Gemtext Output (Auto-generated):**

```gemtext
# Welcome to Slate

Slate is a static site generator designed for simplicity.

## Features
* Bold, Italic, Strikethrough
=> https://example.com Links
* Item 1
* Item 2

> [NOTE]
> This is a callout.
```
