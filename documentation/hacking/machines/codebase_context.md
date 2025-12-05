# Codebase Context

Slate is a static site generator that supports multiple output formats: HTML, Gemtext, and Gopher.

## Core Architecture

1.  **Discovery (`site.py`)**: The site structure is discovered from the file system, starting from `index.md`. It builds a graph of `Page` and `Category` objects.
2.  **Parsing (`parse.py`)**: Markdown files are parsed into a list of block dictionaries using `markdown-it-py`.
3.  **Rendering (`render.py`)**: The block dictionaries are rendered into the target format using specific renderers (`HTMLRenderer`, `GemtextRenderer`, `GopherRenderer`).
4.  **CLI (`main.py`)**: The CLI orchestrates the build process, handling arguments and invoking the discovery, parsing, and rendering steps.
5.  **Link Resolution**: `render.py` contains `resolve_link`, a centralized function for handling relative links and format conversion (e.g., `.md` to `.html` or `.gmi`), crucial for IPFS compatibility.
6.  **Blog Listing**: `navigation.py` generates granular blog variables (`blog_title`, `blog_description`, `blog_view`, `blog_content`) for flexible template rendering.
7.  **TOC Generation**: `parse.py` generates the Table of Contents, and `render.py` ensures headings have unique IDs matching the TOC links.

## Key Libraries

-   `markdown-it-py`: Markdown parsing.
-   `jinja2`: HTML templating.
-   `rich`: CLI output and progress bars.
-   `pyyaml`: Frontmatter parsing.
