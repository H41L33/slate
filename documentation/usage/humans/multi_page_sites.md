# Building Multi-Page Sites with Slate

This guide shows you how to use Slate v0.2.0 to build organized multi-page sites with auto-generated navigation and RSS feeds.

## What You'll Build

By the end of this guide, you'll have a site with:
- Home page
- Blog with multiple posts
- Projects section
- Auto-generated navigation
- RSS feed for your blog

## Site Structure

Slate organizes sites using a simple folder structure:

```
my-site/
├── index.md              ← Your home page (defines categories)
├── blog.md               ← Blog category root
├── blog/
│   ├── first-post.md
│   ├── second-post.md
│   └── feed.xml          ← Auto-generated!
├── projects.md           ← Projects category root
├── projects/
│   └── slate.md
└── templates/
    └── default.html
```

## Step-by-Step Tutorial

### 1. Create Your Home Page

Create `index.md` with frontmatter:

```yaml
---
categories: [blog, projects]
title: My Awesome Site
url: https://example.com
template: templates/default.html
description: Welcome to my site
---

# Welcome!

This is my home page. Check out my blog and projects!
```

**Important frontmatter fields:**
- `categories` - List of site sections (each becomes a category)
- `url` - Your site's base URL (for RSS feeds)
- `template` - Path to your HTML template

### 2. Create Category Root Pages

Each category needs a root page.

Create `blog.md`:

```yaml
---
title: Blog
template: templates/default.html
description: My thoughts and writings
---

# Blog

Welcome to my blog! Here are my latest posts:

{{nav_category}}
```

Create `projects.md`:

```yaml
---
title: Projects
template: templates/default.html
description: Things I've built
---

# Projects

Here's what I've been working on:

{{nav_category}}
```

**The magic:** `{{nav_category}}` gets replaced with a list of all pages in that category!

### 3. Create Blog Posts

Create `blog/first-post.md`:

```yaml
---
title: My First Post
type: blog
date: 2024-12-01
author: Your Name
template: templates/default.html
description: My very first blog post
---

# My First Post

This is my first post using Slate!

Here's what I learned[^1].

[^1]: Slate makes static sites super easy!
```

**Blog post requirements:**
- `type: blog` - Marks this as a blog post (for RSS)
- `date` - Required for blog posts (YYYY-MM-DD format)
- `title` - Required for blog posts

Create `blog/second-post.md` the same way (with a different date).

### 4. Create Project Pages

Create `projects/slate.md`:

```yaml
---
title: Slate Static Site Generator
template: templates/default.html
description: A hackable static site generator
---

# Slate

Slate is a simple, hackable static site generator I'm using to build this site!

## Table of Contents

{{toc}}

## Features

- Simple and hackable
- Multi-format output
- Auto-generated navigation

## Why I Built It

...
```

### 5. Use the Default Template

Copy the default template:

```bash
# If you have Slate installed from source:
cp templates/default.html my-site/templates/

# Or create your own minimal template (see Template Guide)
```

### 6. Build Your Site!

```bash
cd my-site
slate rebuild
```

That's it! Slate will:
- ✅ Build `index.html`
- ✅ Build `blog.html` and `projects.html`  
- ✅ Build all blog posts and projects
- ✅ Generate `blog/feed.xml` for your RSS feed
- ✅ Add navigation links to all pages
- ✅ Generate table of contents where you used `{{toc}}`

## What Gets Generated

After running `slate rebuild`:

```
my-site/
├── index.html            ← Home page with nav
├── blog.html             ← Blog index with post list
├── blog/
│   ├── first-post.html
│   ├── second-post.html
│   └── feed.xml          ← RSS feed!
├── projects.html         ← Projects index
└── projects/
    └── slate.html
```

## Template Variables Available

Your templates have access to these variables:

### Content
- `{{content}}` - Your rendered Markdown
- `{{title}}` - Page title
- `{{description}}` - Page description

### Navigation (NEW in v0.2.0)
- `{{nav_header}}` - Links to all categories
- `{{nav_category}}` - Links to pages in current category
- `{{breadcrumbs}}` - Breadcrumb navigation
- `{{category_name}}` - Current category name

### Enhancements
- `{{toc}}` - Auto-generated table of contents
- Footnotes are automatically processed!

### Metadata
- `{{creation_date}}` / `{{creation_time}}`
- `{{modify_date}}` / `{{modify_time}}`
- `{{version}}` - Slate version

## RSS Feeds

Slate automatically generates RSS feeds for categories with blog posts (posts with `type: blog`).

Your feed will be at: `blog/feed.xml`

Readers can subscribe at: `https://example.com/blog/feed.xml`

## Tips & Tricks

### Organizing Content

- Keep all blog posts in `blog/` folder
- Use descriptive filenames: `my-great-post.md`
- Add dates to frontmatter for proper sorting

### Navigation Customization

Navigation is auto-generated but you can customize the HTML/CSS:
- Style `.toc` class for table of contents
- Style navigation links in your CSS
- Override in your template

### Working with Drafts

Want to work on a post without publishing it?
- Keep it outside the `blog/` folder
- Remove it from the folder before running `slate rebuild`

## Next Steps

- **Customize your template:** See [Template Customization](template_guide.md)
- **Learn frontmatter:** See [Frontmatter Reference](frontmatter_reference.md)
- **Deploy your site:** Upload the HTML files to any static host!

---

**Questions?** Check out the other guides or [open an issue](https://github.com/H41L33/slate/issues).
