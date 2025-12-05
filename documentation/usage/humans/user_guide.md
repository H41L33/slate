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


## Blog Posts

To create a blog post, set the `type` in the frontmatter to `blog-post`. You must also provide a `date`.

```yaml
---
title: My First Post
date: 2024-12-05
type: blog-post
description: This is a description.
---
```

### Blog Listing Variables

Slate provides granular variables to list blog posts in your templates. These lists are synchronized (same index corresponds to the same post) and sorted by date (newest first).

-   `{{ blog_title }}`: List of titles.
-   `{{ blog_description }}`: List of descriptions.
-   `{{ blog_view }}`: List of links to the post (format-aware: `.html`, `.gmi`, or `.txt`).
-   `{{ blog_content }}`: List of links to the raw Markdown content.

You can use the `zip` function to iterate over them together:

```jinja2
{% for title, desc, link, content in zip(blog_title, blog_description, blog_view, blog_content) %}
<article>
  <h2><a href="{{ link }}">{{ title }}</a></h2>
  <p>{{ desc }}</p>
  <a href="{{ content }}">Download Source</a>
</article>
{% endfor %}
```

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
