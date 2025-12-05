# Slate User Guide

Slate is a static site generator designed for the modern (and retro) web. It supports HTML, Gemini, and Gopher.

## Getting Started

1.  **Install Slate**:
    ```bash
    pipx install slate-md
    ```

2.  **Create a Site**:
    Create a directory with an `index.md` file.

    ```markdown
    ---
    title: My Site
    categories: [blog]
    ---
    # Welcome to My Site
    ```


3.  **Build the Site**:
    ```bash
    slate build .
    ```

4.  **Rapid Iteration**:
    Use `slate rebuild` to re-run your last command quickly.

    ```bash
    slate rebuild
    ```

## Commands Overview

-   `slate draft <name>`: Create a new site.
-   `slate build [target]`: Build your site.
-   `slate rebuild`: Re-run the last command.


## Site Structure

-   `index.md`: The entry point. Defines categories in frontmatter.
-   `{category}.md`: The root page for a category (e.g., `blog.md`).
-   `{category}/`: Directory containing pages for that category.

## Frontmatter

Slate uses YAML frontmatter.

```yaml
---
title: Page Title
description: A brief description.
date: 2024-01-01
type: blog  # Optional: 'blog' for blog posts
---
```

## Multi-Protocol Support

Slate generates HTML by default. To generate Gemini and Gopher sites:

```bash
slate build . --formats html,gemini,gopher
```
