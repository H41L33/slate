"""Tests for site structure discovery."""

import pytest
import tempfile
from pathlib import Path

from slate.site import (
    discover_site,
    validate_site_structure,
    Page,
    Category,
    Site,
)


class TestSiteDiscovery:
    """Test site structure discovery."""
    
    def setup_method(self):
        """Create temporary directory for test sites."""
        self.temp_dir = tempfile.mkdtemp()
        self.root = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_discover_simple_site(self):
        """Test discovering a simple site with one category."""
        # Create index.md
        (self.root / "index.md").write_text("""---
categories: [blog]
title: My Site
---

Welcome to my site!
""")
        
        # Create blog.md (category root)
        (self.root / "blog.md").write_text("""---
title: Blog
---

Blog posts below.
""")
        
        # Create blog directory with one post
        (self.root / "blog").mkdir()
        (self.root / "blog" / "post1.md").write_text("""---
title: First Post
type: blog
date: 2024-12-01
---

My first post!
""")
        
        site = discover_site(self.root)
        
        assert site.root_path.resolve() == self.root.resolve()
        assert site.index_page.title == "My Site"
        assert len(site.categories) == 1
        assert "blog" in site.categories
        
        blog = site.categories["blog"]
        assert blog.name == "blog"
        assert blog.root_page.title == "Blog"
        assert len(blog.pages) == 1
        assert blog.pages[0].title == "First Post"
        assert blog.pages[0].is_blog_post
    
    def test_discover_multi_category_site(self):
        """Test discovering a site with multiple categories."""
        # Create index.md with multiple categories
        (self.root / "index.md").write_text("""---
categories: [blog, projects]
---

# Welcome
""")
        
        # Create blog category
        (self.root / "blog.md").write_text("---\ntitle: Blog\n---\n")
        (self.root / "blog").mkdir()
        (self.root / "blog" / "post1.md").write_text("""---
title: Post 1
type: blog
date: 2024-12-01
---
""")
        
        # Create projects category
        (self.root / "projects.md").write_text("---\ntitle: Projects\n---\n")
        (self.root / "projects").mkdir()
        (self.root / "projects" / "slate.md").write_text("""---
title: Slate
type: page
---
""")
        
        site = discover_site(self.root)
        
        assert len(site.categories) == 2
        assert "blog" in site.categories
        assert "projects" in site.categories
        assert len(site.categories["blog"].pages) == 1
        assert len(site.categories["projects"].pages) == 1
    
    def test_missing_index(self):
        """Test error when index.md is missing."""
        with pytest.raises(FileNotFoundError, match="index.md"):
            discover_site(self.root)
    
    def test_missing_category_root(self):
        """Test error when category root page is missing."""
        (self.root / "index.md").write_text("""---
categories: [blog]
---
""")
        
        # No blog.md created
        
        with pytest.raises(FileNotFoundError, match="blog.md"):
            discover_site(self.root)
    
    def test_invalid_categories_type(self):
        """Test error when categories is not a list."""
        (self.root / "index.md").write_text("""---
categories: blog
---
""")
        
        with pytest.raises(ValueError, match="must be a list"):
            discover_site(self.root)
    
    def test_blog_post_sorting(self):
        """Test blog posts are sorted by date (newest first)."""
        (self.root / "index.md").write_text("---\ncategories: [blog]\n---\n")
        (self.root / "blog.md").write_text("---\ntitle: Blog\n---\n")
        (self.root / "blog").mkdir()
        
        # Create posts with different dates
        (self.root / "blog" / "old.md").write_text("""---
title: Old Post
type: blog
date: 2024-01-01
---
""")
        
        (self.root / "blog" / "new.md").write_text("""---
title: New Post
type: blog
date: 2024-12-01
---
""")
        
        (self.root / "blog" / "middle.md").write_text("""---
title: Middle Post
type: blog
date: 2024-06-01
---
""")
        
        site = discover_site(self.root)
        blog = site.categories["blog"]
        posts = blog.blog_posts
        
        assert len(posts) == 3
        assert posts[0].title == "New Post"
        assert posts[1].title == "Middle Post"
        assert posts[2].title == "Old Post"
    
    def test_category_mismatch(self):
        """Test error when frontmatter category doesn't match directory."""
        (self.root / "index.md").write_text("---\ncategories: [blog]\n---\n")
        (self.root / "blog.md").write_text("---\ntitle: Blog\n---\n")
        (self.root / "blog").mkdir()
        
        # Page in blog/ with wrong category in frontmatter
        (self.root / "blog" / "post.md").write_text("""---
title: Post
category: projects
---
""")
        
        with pytest.raises(ValueError, match="doesn't match directory"):
            discover_site(self.root)
    
    def test_invalid_blog_post(self):
        """Test error when blog post is missing required fields."""
        (self.root / "index.md").write_text("---\ncategories: [blog]\n---\n")
        (self.root / "blog.md").write_text("---\ntitle: Blog\n---\n")
        (self.root / "blog").mkdir()
        
        # Blog post without date
        (self.root / "blog" / "post.md").write_text("""---
title: Post
type: blog
---
""")
        
        with pytest.raises(ValueError, match="require 'date'"):
            discover_site(self.root)
    
    def test_empty_category(self):
        """Test category with no pages (just root)."""
        (self.root / "index.md").write_text("---\ncategories: [blog]\n---\n")
        (self.root / "blog.md").write_text("---\ntitle: Blog\n---\n")
        # No blog/ directory
        
        site = discover_site(self.root)
        
        assert "blog" in site.categories
        assert len(site.categories["blog"].pages) == 0
        
        warnings = validate_site_structure(site)
        assert any("no pages" in w for w in warnings)


class TestPageDataclass:
    """Test Page dataclass properties."""
    
    def test_page_title_from_frontmatter(self):
        """Test title comes from frontmatter."""
        page = Page(
            source_path=Path("post.md"),
            output_path=Path("post.html"),
            frontmatter={"title": "My Post"},
            category="blog",
            is_category_root=False
        )
        assert page.title == "My Post"
    
    def test_page_title_from_filename(self):
        """Test title falls back to filename."""
        page = Page(
            source_path=Path("my-cool-post.md"),
            output_path=Path("my-cool-post.html"),
            frontmatter={},
            category="blog",
            is_category_root=False
        )
        assert page.title == "My Cool Post"
    
    def test_is_blog_post(self):
        """Test blog post detection."""
        blog_page = Page(
            source_path=Path("post.md"),
            output_path=Path("post.html"),
            frontmatter={"type": "blog", "date": "2024-12-01"},
            category="blog",
            is_category_root=False
        )
        assert blog_page.is_blog_post
        
        regular_page = Page(
            source_path=Path("about.md"),
            output_path=Path("about.html"),
            frontmatter={"type": "page"},
            category="pages",
            is_category_root=False
        )
        assert not regular_page.is_blog_post


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
