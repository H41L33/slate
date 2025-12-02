"""Navigation generation for Slate sites.

This module generates navigation HTML for multi-page sites,
including header navigation and category-specific navigation.
"""

from typing import Any

from slate.site import Category, Site


class NavigationGenerator:
    """Generates navigation HTML for templates."""
    
    @staticmethod
    def generate_header_nav(site: Site) -> str:
        """Generate header navigation linking to all category root pages.
        
        This creates a simple list of links to each category root page.
        Templates can style this however they want.
        
        Args:
            site: The Site object with categories
            
        Returns:
            HTML string with navigation links
            
        Example output:
            <a href="blog.html">Blog</a>
            <a href="projects.html">Projects</a>
        """
        links = []
        for cat_name, category in sorted(site.categories.items()):
            label = category.root_page.title
            href = f"{cat_name}.html"
            links.append(f'<a href="{href}">{label}</a>')
        
        return '\n'.join(links)
    
    @staticmethod
    def generate_category_nav(category: Category) -> str:
        """Generate category-specific navigation for pages within a category.
        
        Creates an unordered list of links to all pages in the category.
        For blog categories, shows blog posts in date order (newest first).
        
        Args:
            category: The Category object
            
        Returns:
            HTML string with navigation list
            
        Example output:
            <ul>
              <li><a href="blog/post1.html">First Post</a></li>
              <li><a href="blog/post2.html">Second Post</a></li>
            </ul>
        """
        if not category.pages:
            return ""
        
        # Use blog posts if category has them (sorted by date)
        pages_to_show = category.blog_posts if category.blog_posts else category.pages
        
        links = []
        for page in pages_to_show:
            title = page.title
            # Make href relative to category root
            href = page.output_path.name if not page.is_category_root else "#"
            
            # For blog posts, optionally include date
            if page.is_blog_post and "date" in page.frontmatter:
                date = page.frontmatter["date"]
                # Format date (handle both datetime.date and string)
                date_str = str(date) if hasattr(date, '__str__') else date
                links.append(f'  <li><a href="{href}">{title}</a> <span class="date">({date_str})</span></li>')
            else:
                links.append(f'  <li><a href="{href}">{title}</a></li>')
        
        return '<ul>\n' + '\n'.join(links) + '\n</ul>'
    
    @staticmethod
    def generate_breadcrumbs(page_category: str | None, site: Site, current_page: Any = None) -> str:
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

        # Start with Home
        crumbs = [('<a href="/" class="breadcrumb-link">Home</a>', '/')]
        
        # Add Category if present
        if page_category and page_category in site.categories:
            cat = site.categories[page_category]
            # Use absolute path /category.html or /pages/category.html depending on structure?
            # Actually, we should probably use relative paths or resolved absolute paths.
            # But for simplicity, let's assume the link generator handles it or we use the output name.
            # Wait, we need the href.
            # If we are in tree structure, it might be /pages/blog.html.
            # If flat, /blog.html.
            # We can use the output_path.name but that's relative to output root.
            # Let's try to be smart.
            
            # Note: We don't know the structure here easily without site config or checking paths.
            # But we can use the category root page's output path name?
            # No, that's just filename.
            
            # Let's rely on the fact that we are generating static site.
            # We can use relative paths if we knew where we are.
            # But here we return a string.
            
            # Let's just use the filename for now, assuming flat or simple tree.
            # Or better: use the relative path from output root.
            # But we don't have output root here.
            
            # Let's assume standard links for now.
            # cat_href = f"{page_category}.html"  <-- Removed unused variable
            # If tree, it might be pages/category.html.
            # This is tricky without context.
            
            # However, the user asked for "identical <a> tags".
            # Let's just output the link to the category root.
            
            # If we have the current page, we can calculate relative path?
            # No, let's just use the category name for now.
            
            crumbs.append((f'<a href="{cat.root_page.output_path.name}" class="breadcrumb-link">{cat.root_page.title}</a>', cat.root_page.output_path.name))
            
        # Add Current Page if it's not the category root
        if current_page:
            is_cat_root = False
            if page_category and page_category in site.categories and site.categories[page_category].root_page == current_page:
                is_cat_root = True
            
            if not is_cat_root and current_page != site.index_page:
                 # For the current page, we might not want a link, or a link to self.
                 # User asked for "identical <a> tags".
                 # So we link to self.
                 crumbs.append((f'<a href="{current_page.output_path.name}" class="breadcrumb-link current">{current_page.title}</a>', current_page.output_path.name))

        # Join with separator
        separator = ' <span class="breadcrumb-separator">/</span> '
        html = separator.join(c[0] for c in crumbs)
        
        return f'<nav class="breadcrumbs">{html}</nav>'


def build_navigation_context(site: Site, current_category: str | None = None, current_page: Any = None) -> dict[str, Any]:
    """Build navigation context dictionary for template rendering.
    
    This creates a context dict with all navigation-related variables
    that can be injected into templates.
    
    Args:
        site: The Site object
        current_category: Category of the current page (None for index)
        current_page: The current Page object (optional)
        
    Returns:
        Dictionary with navigation variables:
        - nav_header: Header navigation HTML
        - nav_category: Category navigation HTML (if in a category)
        - category_name: Name of current category (if in a category)
        - breadcrumbs: Breadcrumb navigation HTML
    """
    nav_gen = NavigationGenerator()
    
    context = {
        "nav_header": nav_gen.generate_header_nav(site),
        "nav_category": "",
        "category_name": current_category or "",
        "breadcrumbs": nav_gen.generate_breadcrumbs(current_category, site, current_page),
    }
    
    # Add category-specific navigation if in a category
    if current_category and current_category in site.categories:
        category = site.categories[current_category]
        context["nav_category"] = nav_gen.generate_category_nav(category)
    
    return context
