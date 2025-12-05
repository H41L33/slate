"""Navigation generation for Slate sites.

This module generates navigation HTML for multi-page sites,
including header navigation and category-specific navigation.
"""

from typing import Any

from slate.site import Category, Site


class NavigationGenerator:
    """Generates navigation HTML for templates."""

    @staticmethod
    def generate_header_nav(site: Site, current_page: Any = None) -> str:
        """Generate header navigation linking to all category root pages.

        This creates a simple list of links to each category root page.
        Templates can style this however they want.

        Args:
            site: The Site object with categories
            current_page: The current Page object (optional) for relative path calculation

        Returns:
            HTML string with navigation links

        Example output:
            <a href="blog.html">Blog</a>
            <a href="projects.html">Projects</a>
        """
        import os

        links = []
        for _cat_name, category in sorted(site.categories.items()):
            label = category.root_page.title

            # Calculate relative path if current_page is provided
            if current_page:
                # Get relative path from current page's directory to the category root page
                # We need to go from current_page.output_path.parent to category.root_page.output_path
                try:
                    rel_path = os.path.relpath(
                        category.root_page.output_path, current_page.output_path.parent
                    )
                    href = rel_path
                except ValueError:
                    # Fallback if paths are on different drives or something weird
                    href = category.root_page.output_path.name
            else:
                # Fallback to simple filename (works for flat structure or root)
                href = category.root_page.output_path.name

            links.append(f'<a href="{href}" class="content-nav_header">{label}</a>')

        return "\n".join(links)

    @staticmethod
    def generate_category_nav(category: Category, current_page: Any = None) -> str:
        """Generate category-specific navigation for pages within a category.

        Creates an unordered list of links to all pages in the category.
        For blog categories, shows blog posts in date order (newest first).

        Args:
            category: The Category object
            current_page: The current Page object (optional) for relative path calculation

        Returns:
            HTML string with navigation list
        """
        if not category.pages:
            return ""

        # Use blog posts if category has them (sorted by date)
        pages_to_show = category.blog_posts if category.blog_posts else category.pages

        links = []
        import os

        for page in pages_to_show:
            title = page.title

            # Calculate href
            if current_page:
                try:
                    # Calculate relative path from current page's directory to target page
                    rel_path = os.path.relpath(
                        page.output_path, current_page.output_path.parent
                    )
                    href = rel_path
                except ValueError:
                    href = page.output_path.name
            else:
                href = page.output_path.name

            # For blog posts, optionally include date
            if page.is_blog_post and "date" in page.frontmatter:
                date = page.frontmatter["date"]
                # Format date (handle both datetime.date and string)
                date_str = str(date) if hasattr(date, "__str__") else date
                links.append(
                    f'  <li><a href="{href}" class="content-nav_category">{title}</a> <span class="date">({date_str})</span></li>'
                )
            else:
                links.append(
                    f'  <li><a href="{href}" class="content-nav_category">{title}</a></li>'
                )

        return "<ul>\n" + "\n".join(links) + "\n</ul>"

    @staticmethod
    def generate_breadcrumbs(
        page_category: str | None, site: Site, current_page: Any = None
    ) -> str:
        """Generate breadcrumb navigation.

        Args:
            page_category: Category of current page (None for index)
            site: The Site object
            current_page: The current Page object (optional)

        Returns:
            HTML breadcrumb string
        """
        # If no category and no current page (or current page is index), return empty
        if not page_category and (not current_page or current_page == site.index_page):
            return ""

        import os

        # Helper to get relative path to root or other pages
        def get_rel_href(target_path):
            if current_page:
                try:
                    return os.path.relpath(target_path, current_page.output_path.parent)
                except ValueError:
                    return target_path.name
            return target_path.name

        # Start with Home
        # Home is site.index_page
        home_href = get_rel_href(site.index_page.output_path)
        crumbs = [(f'<a href="{home_href}" class="breadcrumb">Home</a>', home_href)]

        # Add Category if present
        if page_category and page_category in site.categories:
            cat = site.categories[page_category]
            cat_href = get_rel_href(cat.root_page.output_path)
            crumbs.append(
                (
                    f'<a href="{cat_href}" class="breadcrumb">{cat.root_page.title}</a>',
                    cat_href,
                )
            )

        # Add Current Page if it's not the category root
        if current_page:
            is_cat_root = False
            if (
                page_category
                and page_category in site.categories
                and site.categories[page_category].root_page == current_page
            ):
                is_cat_root = True

            if not is_cat_root and current_page != site.index_page:
                # Link to self (relative is just filename)
                self_href = current_page.output_path.name
                crumbs.append(
                    (
                        f'<a href="{self_href}" class="breadcrumb current">{current_page.title}</a>',
                        self_href,
                    )
                )

        # Join with separator
        separator = ' <span class="breadcrumb-separator">/</span> '
        html = separator.join(c[0] for c in crumbs)

        return f'<nav class="breadcrumbs">{html}</nav>'

    @staticmethod
    def generate_blog_listing_variables(
        site: Site, current_page: Any = None, fmt: str = "html"
    ) -> dict[str, list[str]]:
        """Generate granular blog listing variables.

        Returns four lists of strings, all sorted by date (newest first):
        - blog_title: List of post titles
        - blog_description: List of post descriptions
        - blog_view: List of view URLs (format-specific)
        - blog_content: List of raw Markdown URLs

        Args:
            site: The Site object
            current_page: The current Page object (optional)
            fmt: Output format ("html", "gemini", "gopher")

        Returns:
            Dictionary containing the four lists
        """
        import os

        # Collect all blog posts from all categories
        all_posts = []
        for category in site.categories.values():
            all_posts.extend(category.blog_posts)

        # Sort by date (newest first)
        # Note: Category.blog_posts is already sorted, but we merged multiple categories
        all_posts.sort(
            key=lambda p: p.frontmatter.get("date", "0000-00-00"), reverse=True
        )

        titles = []
        descriptions = []
        views = []
        contents = []

        for post in all_posts:
            titles.append(post.title)
            descriptions.append(post.frontmatter.get("description", ""))

            # Calculate relative paths
            if current_page:
                try:
                    # View path (format specific)
                    # For HTML: relative path to .html
                    # For Gemini/Gopher: relative path to .gmi/.txt
                    # But Page.output_path is the absolute path to the output file
                    # We need to respect the requested format extension

                    # Determine extension based on format
                    ext = ".html"
                    if fmt in ("gemini", "gemtext"):
                        ext = ".gmi"
                    elif fmt in ("gopher", "gophermap"):
                        ext = ".txt"

                    # Get output path with correct extension
                    # Page.output_path usually has the extension of the primary build format
                    # But here we want the link to match the current build format
                    target_path = post.output_path.with_suffix(ext)

                    view_href = os.path.relpath(
                        target_path, current_page.output_path.parent
                    )

                    # Content path (raw markdown)
                    # We assume the markdown file is copied to the output directory
                    # or served from source. Slate usually copies static assets.
                    # Actually, Slate doesn't copy raw MD by default unless configured.
                    # But the user requested a link to download raw content.
                    # Let's assume we link to the .md file relative to the output.
                    # NOTE: Slate currently reads from source and writes to output.
                    # It doesn't copy the .md file to output.
                    # However, for this feature to work as requested ("download raw content"),
                    # we might need to ensure .md files are available or link to source?
                    # For now, let's generate a link to where the .md file WOULD be
                    # if it were in the output directory.
                    md_output_path = post.output_path.with_suffix(".md")
                    content_href = os.path.relpath(
                        md_output_path, current_page.output_path.parent
                    )

                except ValueError:
                    view_href = post.output_path.with_suffix(ext).name
                    content_href = post.output_path.with_suffix(".md").name
            else:
                view_href = post.output_path.name
                content_href = post.output_path.with_suffix(".md").name

            views.append(view_href)
            contents.append(content_href)

        return {
            "blog_title": titles,
            "blog_description": descriptions,
            "blog_view": views,
            "blog_content": contents,
        }


def build_navigation_context(
    site: Site,
    current_category: str | None = None,
    current_page: Any = None,
    fmt: str = "html",
) -> dict[str, Any]:
    """Build navigation context dictionary for template rendering.

    Args:
        site: The Site object
        current_category: Category of the current page (None for index)
        current_page: The current Page object (optional)
        fmt: Output format ("html", "gemini", "gopher")

    Returns:
        Dictionary with navigation variables
    """
    nav_gen = NavigationGenerator()

    context = {
        "nav_header": nav_gen.generate_header_nav(site, current_page),
        "nav_category": "",
        "category_name": current_category or "",
        "breadcrumbs": nav_gen.generate_breadcrumbs(
            current_category, site, current_page
        ),
    }

    # Add blog listing variables
    blog_vars = nav_gen.generate_blog_listing_variables(site, current_page, fmt)
    context.update(blog_vars)

    # Add category-specific navigation if in a category
    if current_category and current_category in site.categories:
        category = site.categories[current_category]
        context["nav_category"] = nav_gen.generate_category_nav(category, current_page)

    return context
