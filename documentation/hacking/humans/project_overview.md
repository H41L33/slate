# Slate Project Overview

Welcome to Slate! This document explains what Slate is, why it exists, and what makes it special.

## What is Slate?

Slate is a lightweight static site generator that converts Markdown documents into accessible HTML, Gemtext (for the Gemini protocol), and Gopher-formatted text. Think of it as a simple tool that takes your Markdown files and turns them into beautiful, semantic websites—without all the complexity of modern web frameworks.

## Why Did We Build Slate?

Most static site generators have become incredibly complex. They require configuration files, build pipelines, plugin ecosystems, and often come with a steep learning curve. We wanted something different:

- **No configuration files**: Everything is done through the command line or embedded in your content
- **One CSS file**: Designed to work with a single, simple stylesheet
- **Accessible by default**: Proper semantic HTML5 with ARIA attributes
- **Multi-format support**: Your content works on the web, Gemini, and Gopher

## Core Philosophy

Slate follows the **KISS principle** (Keep It Simple, Stupid). We believe:

1. **Simplicity beats features**: We'd rather have 10 features that work perfectly than 100 features that kind of work
2. **Reliability matters**: Your builds should be predictable and consistent
3. **Accessibility isn't optional**: Everyone deserves access to your content
4. **You own your content**: No lock-in, no proprietary formats

## What Can You Build with Slate?

Slate is perfect for:

- **Personal blogs**: Simple, fast, and accessible
- **Knowledge bases**: Documentation that's easy to navigate
- **Small websites**: Portfolio sites, project pages, etc.
- **Alternative protocols**: Share content on Gemini and Gopher networks

Slate is **not** designed for:

- Large-scale corporate websites
- E-commerce platforms
- Sites requiring complex interactivity
- Projects needing asset pipelines or bundling

## Current Features (v0.1.6)

### Markdown to Multiple Formats

Write once in Markdown, output to:
- **HTML**: With Jinja2 templates for full customization
- **Gemtext**: For the Gemini protocol
- **Gopher**: For gopherspace enthusiasts

### Smart Updates

One of Slate's coolest features! Once you've built a file, Slate remembers where it came from. Just run:

```bash
slate update mypage.html
```

No need to re-specify the source file or template—Slate reads the metadata and regenerates the page.

### Dynamic Links

Use the `[!MD-PAGE]` token in your Markdown:

```markdown
Check out my [!MD-PAGE] [latest post](posts/2024-review.md)
```

Slate automatically converts the `.md` extension to `.html` in the output, so your links work on your website while your Markdown stays navigable in GitHub or Obsidian.

### Template Variables

Your Jinja2 templates have access to useful variables:

- `{{title}}`: Page title (extracted from first heading or specified via CLI)
- `{{description}}`: Meta description
- `{{creation_date}}` / `{{creation_time}}`: When the page was first created
- `{{modify_date}}` / `{{modify_time}}`: When the page was last updated
- `{{version}}`: The Slate version used to build the page

### Rich Markdown Support

Slate handles all the standard Markdown you'd expect:

- Headings, paragraphs, blockquotes
- Lists (ordered, unordered, nested)
- Code blocks with syntax highlighting
- Images with captions
- Tables
- Inline code, links, and images

Plus some extras:

- **Callouts**: `[!NOTE]`, `[!WARNING]`, `[!DANGER]`, `[!SUCCESS]`, `[!TIP]`
- **Custom tokens**: Extensible system for adding your own

## How It Works

Slate's pipeline is straightforward:

1. **Parse**: Convert Markdown to structured blocks
2. **Render**: Transform blocks into your target format
3. **Apply template**: Inject content into your Jinja2 template (HTML only)
4. **Save**: Write the result to disk

That's it. No compilation steps, no asset compilation, no dependency graphs.

## Getting Started

Install Slate (we recommend pipx):

```bash
pipx install slate-md
```

Create a simple template (`template.html`):

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
    <meta name="description" content="{{description}}">
</head>
<body>
    {{content}}
</body>
</html>
```

Write some Markdown (`post.md`):

```markdown
# Hello World

This is my first Slate page!
```

Build it:

```bash
slate build post.md post.html -T template.html -t "My First Page"
```

Update it later:

```bash
slate update post.html
```

## What Makes Slate Different?

Most static site generators are "batteries included"—they come with themes, plugins, asset pipelines, and tons of features. Slate is "battery not included"—it does one thing (convert Markdown to formatted output) and does it well.

This means:
- ✅ Faster builds
- ✅ Easier to understand
- ✅ Fewer dependencies
- ✅ More predictable behavior
- ❌ No built-in themes
- ❌ No plugin marketplace
- ❌ No asset processing

If you need those features, other tools like Hugo, Jekyll, or Eleventy might be better fits. But if you want something simple and transparent, Slate is for you.

## Project Values

1. **Transparency**: You should be able to understand what Slate does by reading the code
2. **Stability**: Features land when they're ready, not when they're "good enough"
3. **Accessibility**: Semantic HTML isn't negotiable
4. **Simplicity**: Complexity is a last resort, not a first option

## License

Slate is licensed under LGPL v3, which means:
- ✅ You can use it commercially
- ✅ You can modify it
- ✅ You must share modifications if you distribute them
- ✅ Your content and templates remain yours

## Community

Slate is a small project, and that's intentional. We're not trying to be everything to everyone. If you value simplicity and reliability over feature count, welcome aboard!

---

**Next Steps**:
- Read the [Codebase Guide](codebase_guide.md) to understand the architecture
- Check the [Development Setup](development_setup.md) to start contributing
- Review the [CI Workflow](ci_workflow.md) to learn our quality standards
