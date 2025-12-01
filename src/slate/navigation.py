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
    def generate_breadcrumbs(page_category: str | None, site: Site) -> str:
        """Generate breadcrumb navigation.
        
        Args:
            page_category: Category of current page (None for index)
            site: The Site object
            
        Returns:
            HTML breadcrumb string
            
        Example output:
            <nav class="breadcrumbs">
              <a href="index.html">Home</a> &gt; <span>Blog</span>
            </nav>
        """
        if not page_category:
            # On index page, no breadcrumbs
            return ""
        
        parts = [
            '<nav class="breadcrumbs">',
            '  <a href="index.html">Home</a>',
        ]
        
        if page_category in site.categories:
            cat = site.categories[page_category]
            parts.append(f' &gt; <span>{cat.root_page.title}</span>')
        
        parts.append('</nav>')
        return '\n'.join(parts)


def build_navigation_context(site: Site, current_category: str | None = None) -> dict[str, Any]:
    """Build navigation context dictionary for template rendering.
    
    This creates a context dict with all navigation-related variables
    that can be injected into templates.
    
    Args:
        site: The Site object
        current_category: Category of the current page (None for index)
        
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
        "breadcrumbs": nav_gen.generate_breadcrumbs(current_category, site),
    }
    
    # Add category-specific navigation if in a category
    if current_category and current_category in site.categories:
        category = site.categories[current_category]
        context["nav_category"] = nav_gen.generate_category_nav(category)
    
    return context
