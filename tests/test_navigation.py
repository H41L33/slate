"""Tests for navigation generation."""

from datetime import date
from pathlib import Path

import pytest

from slate.navigation import NavigationGenerator, build_navigation_context
from slate.site import Category, Page, Site


class TestNavigationGenerator:
    """Test navigation HTML generation."""
    
    def test_generate_header_nav(self):
        """Test header navigation generation."""
        # Create mock site with two categories
        blog_page = Page(
            source_path=Path("blog.md"),
            output_path=Path("blog.html"),
            frontmatter={"title": "My Blog"},
            category="blog",
            is_category_root=True
        )
        
        projects_page = Page(
            source_path=Path("projects.md"),
            output_path=Path("projects.html"),
            frontmatter={"title": "Projects"},
            category="projects",
            is_category_root=True
        )
        
        site = Site(
            root_path=Path("."),
            index_page=Page(Path("index.md"), Path("index.html"), {}, None, False),
            categories={
                "blog": Category("blog", blog_page, []),
                "projects": Category("projects", projects_page, []),
            }
        )
        
        nav_html = NavigationGenerator.generate_header_nav(site)
        
        assert '<a href="blog.html" class="content-nav_header">My Blog</a>' in nav_html
        assert '<a href="projects.html" class="content-nav_header">Projects</a>' in nav_html
    
    def test_generate_category_nav_with_pages(self):
        """Test category navigation with regular pages."""
        page1 = Page(
            source_path=Path("blog/post1.md"),
            output_path=Path("blog/post1.html"),
            frontmatter={"title": "First Post", "type": "page"},
            category="blog",
            is_category_root=False
        )
        
        page2 = Page(
            source_path=Path("blog/post2.md"),
            output_path=Path("blog/post2.html"),
            frontmatter={"title": "Second Post", "type": "page"},
            category="blog",
            is_category_root=False
        )
        
        root = Page(Path("blog.md"), Path("blog.html"), {"title": "Blog"}, "blog", True)
        category = Category("blog", root, [page1, page2])
        
        nav_html = NavigationGenerator.generate_category_nav(category)
        
        assert '<ul>' in nav_html
        assert '<a href="post1.html" class="content-nav_category">First Post</a>' in nav_html
        assert '<a href="post2.html" class="content-nav_category">Second Post</a>' in nav_html
        assert '</ul>' in nav_html
    
    def test_generate_category_nav_with_blog_posts(self):
        """Test category navigation with blog posts (includes dates)."""
        post1 = Page(
            source_path=Path("blog/old.md"),
            output_path=Path("blog/old.html"),
            frontmatter={"title": "Old Post", "type": "blog", "date": date(2024, 1, 1)},
            category="blog",
            is_category_root=False
        )
        
        post2 = Page(
            source_path=Path("blog/new.md"),
            output_path=Path("blog/new.html"),
            frontmatter={"title": "New Post", "type": "blog", "date": date(2024, 12, 1)},
            category="blog",
            is_category_root=False
        )
        
        root = Page(Path("blog.md"), Path("blog.html"), {"title": "Blog"}, "blog", True)
        category = Category("blog", root, [post1, post2])
        
        nav_html = NavigationGenerator.generate_category_nav(category)
        
        # Blog posts should be sorted by date (newest first)
        assert nav_html.index("New Post") < nav_html.index("Old Post")
        # Should include dates
        assert "2024-12-01" in nav_html
        assert "2024-01-01" in nav_html
        assert 'class="date"' in nav_html
    
    def test_generate_category_nav_empty(self):
        """Test category navigation with no pages."""
        root = Page(Path("blog.md"), Path("blog.html"), {"title": "Blog"}, "blog", True)
        category = Category("blog", root, [])
        
        nav_html = NavigationGenerator.generate_category_nav(category)
        
        assert nav_html == ""
    
    def test_generate_breadcrumbs_index(self):
        """Test breadcrumbs on index page (none shown)."""
        site = Site(
            root_path=Path("."),
            index_page=Page(Path("index.md"), Path("index.html"), {}, None, False),
            categories={}
        )
        
        breadcrumbs = NavigationGenerator.generate_breadcrumbs(None, site)
        assert breadcrumbs == ""
    
    def test_generate_breadcrumbs_category(self):
        """Test breadcrumbs on category page."""
        blog_root = Page(
            source_path=Path("blog.md"),
            output_path=Path("blog.html"),
            frontmatter={"title": "My Blog"},
            category="blog",
            is_category_root=True
        )
        
        site = Site(
            root_path=Path("."),
            index_page=Page(Path("index.md"), Path("index.html"), {}, None, False),
            categories={"blog": Category("blog", blog_root, [])}
        )
        
        breadcrumbs = NavigationGenerator.generate_breadcrumbs("blog", site)
        
        assert 'class="breadcrumbs"' in breadcrumbs
        assert '<a href="/" class="content-breadcrumb">Home</a>' in breadcrumbs
        assert '<a href="blog.html" class="content-breadcrumb">My Blog</a>' in breadcrumbs
        assert '<span class="breadcrumb-separator">/</span>' in breadcrumbs


class TestBuildNavigationContext:
    """Test navigation context building."""
    
    def test_build_context_for_index(self):
        """Test building navigation context for index page."""
        site = Site(
            root_path=Path("."),
            index_page=Page(Path("index.md"), Path("index.html"), {}, None, False),
            categories={
                "blog": Category(
                    "blog",
                    Page(Path("blog.md"), Path("blog.html"), {"title": "Blog"}, "blog", True),
                    []
                )
            }
        )
        
        context = build_navigation_context(site, current_category=None)
        
        assert "nav_header" in context
        assert "blog.html" in context["nav_header"]
        assert context["nav_category"] == ""
        assert context["category_name"] == ""
        assert context["breadcrumbs"] == ""
    
    def test_build_context_for_category_page(self):
        """Test building navigation context for category page."""
        page1 = Page(
            Path("blog/post.md"),
            Path("blog/post.html"),
            {"title": "Post", "type": "page"},
            "blog",
            False
        )
        
        site = Site(
            root_path=Path("."),
            index_page=Page(Path("index.md"), Path("index.html"), {}, None, False),
            categories={
                "blog": Category(
                    "blog",
                    Page(Path("blog.md"), Path("blog.html"), {"title": "Blog"}, "blog", True),
                    [page1]
                )
            }
        )
        
        context = build_navigation_context(site, current_category="blog")
        
        assert "nav_header" in context
        assert context["nav_category"] != ""
        assert "Post" in context["nav_category"]
        assert context["category_name"] == "blog"
        assert "breadcrumbs" in context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
