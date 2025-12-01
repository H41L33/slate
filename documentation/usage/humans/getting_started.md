# Getting Started with Slate

**Welcome!** This guide will help you start building static sites with Slate in minutes.

## What is Slate?

Slate is a lightweight, hackable static site generator that converts Markdown to HTML, Gemtext, and Gopher. It's designed to be **stupid simple** - no complex configurations, just Markdown and templates.

## Installation

### Via pipx (Recommended)

```bash
pipx install slate-md
```

### Via pip

```bash
pip install slate-md
```

### Verify Installation

```bash
slate --help
```

You should see three commands: `build`, `update`, and `rebuild`.

---

## Quick Start: Your First Page

### 1. Create a Markdown File

Create `hello.md`:

```markdown
# Hello, World!

This is my first page built with Slate.

- It's simple
- It's fast
- It's hackable
```

### 2. Create a Template

Create `template.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
</head>
<body>
    <h1>My Site</h1>
    {{content}}
    <footer>Built with Slate</footer>
</body>
</html>
```

### 3. Build Your Page

```bash
slate build hello.md hello.html -T template.html
```

That's it! Open `hello.html` in your browser.

### 4. Update Your Page

Edit `hello.md`, then:

```bash
slate update hello.html
```

Slate remembers the source and template - no need to specify them again!

---

## Next Steps

Now that you've built your first page, you can:

### Option A: Build More Single Pages

Keep using `slate build` and `slate update` to create standalone pages. This is perfect for:
- Simple blogs
- Documentation pages
- Quick static pages

**See:** [Single Page Usage Guide](single_page_usage.md)

### Option B: Build a Multi-Page Site

Use Slate v0.2.0's site management features to create organized sites with:
- Auto-generated navigation
- RSS feeds for blogs
- Consistent layouts across pages
- Table of contents

**See:** [Multi-Page Site Guide](multi_page_sites.md)

---

## Getting Help

- **Documentation:** Check the other guides in this folder
- **Examples:** See `templates/default.html` for a fully-commented template
- **Issues:** [GitHub Issues](https://github.com/H41L33/slate/issues)

---

## Philosophy

Slate follows these principles:

1. **Keep It Simple** - No config files, no magic
2. **Stay Hackable** - Everything is transparent and modifiable
3. **Be Reliable** - Simple code means fewer bugs

Enjoy building! 🚀
