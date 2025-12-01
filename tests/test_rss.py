"""Tests for RSS feed generation."""

from datetime import date
from pathlib import Path

import pytest

from slate.rss import _format_rfc822_date, generate_rss_feed
from slate.site import Category, Page


class TestRSSGeneration:
    """Test RSS feed generation."""
    
    def test_generate_feed_with_blog_posts(self):
        """Test generating RSS feed with blog posts."""
        # Create blog posts
        post1 = Page(
            source_path=Path("blog/old.md"),
            output_path=Path("blog/old.html"),
            frontmatter={
                "title": "Old Post",
                "type": "blog",
                "date": date(2024, 1, 1),
                "description": "An old post",
                "author": "Alice"
            },
            category="blog",
            is_category_root=False
        )
        
        post2 = Page(
            source_path=Path("blog/new.md"),
            output_path=Path("blog/new.html"),
            frontmatter={
                "title": "New Post",
                "type": "blog",
                "date": date(2024, 12, 1),
                "description": "A new post"
            },
            category="blog",
            is_category_root=False
        )
        
        root = Page(
            Path("blog.md"),
            Path("blog.html"),
            {"title": "Blog"},
            "blog",
            True
        )
        
        category = Category("blog", root, [post1, post2])
        
        feed = generate_rss_feed(
            category,
            "https://example.com",
            "My Site",
            "My blog posts"
        )
        
        # Validate feed structure
        assert '<?xml version="1.0" encoding="UTF-8"?>' in feed
        # RSS element might have namespace attributes
        assert '<rss' in feed and 'version="2.0"' in feed
        assert '<channel>' in feed
        assert '<title>My Site - Blog</title>' in feed
        assert '<link>https://example.com/blog.html</link>' in feed
        assert '<description>My blog posts</description>' in feed
        
        # Items should be in reverse chronological order
        assert feed.index("New Post") < feed.index("Old Post")
        
        # Check item details
        assert '<title>New Post</title>' in feed
        assert '<description>A new post</description>' in feed
        assert 'blog/new.html' in feed
        
        assert '<title>Old Post</title>' in feed
        assert '<author>Alice</author>' in feed
        assert 'blog/old.html' in feed
    
    def test_generate_feed_no_blog_posts(self):
        """Test generating RSS feed with no blog posts."""
        root = Page(
            Path("pages.md"),
            Path("pages.html"),
            {"title": "Pages"},
            "pages",
            True
        )
        
        category = Category("pages", root, [])
        
        feed = generate_rss_feed(
            category,
            "https://example.com",
            "My Site"
        )
        
        assert '<?xml version="1.0" encoding="UTF-8"?>' in feed
        assert '<rss' in feed and 'version="2.0"' in feed
        assert '<channel>' in feed
        assert '<title>My Site - Pages</title>' in feed
        # Should have no <item> elements
        assert '<item>' not in feed
    
    def test_format_rfc822_date_from_date_object(self):
        """Test RFC 822 date formatting from date object."""
        test_date = date(2024, 12, 1)
        formatted = _format_rfc822_date(test_date)
        
        assert "01 Dec 2024" in formatted
        assert "+0000" in formatted
    
    def test_format_rfc822_date_from_string(self):
        """Test RFC 822 date formatting from ISO string."""
        formatted = _format_rfc822_date("2024-12-01")
        
        assert "01 Dec 2024" in formatted
        assert "+0000" in formatted
    
    def test_feed_includes_guid(self):
        """Test that RSS feed includes GUID for each post."""
        post = Page(
            source_path=Path("blog/post.md"),
            output_path=Path("blog/post.html"),
            frontmatter={
                "title": "Test Post",
                "type": "blog",
                "date": date(2024, 12, 1)
            },
            category="blog",
            is_category_root=False
        )
        
        root = Page(Path("blog.md"), Path("blog.html"), {"title": "Blog"}, "blog", True)
        category = Category("blog", root, [post])
        
        feed = generate_rss_feed(category, "https://example.com", "Site")
        
        assert '<guid isPermaLink="true">https://example.com/blog/post.html</guid>' in feed
    
    def test_feed_includes_atom_self_link(self):
        """Test that RSS feed includes atom:link for self-reference."""
        root = Page(Path("blog.md"), Path("blog.html"), {"title": "Blog"}, "blog", True)
        category = Category("blog", root, [])
        
        feed = generate_rss_feed(category, "https://example.com", "Site")
        
        assert 'xmlns:atom="http://www.w3.org/2005/Atom"' in feed
        # Might be ns0:link or atom:link depending on XML library
        assert 'link href="https://example.com/blog/feed.xml"' in feed
        assert 'rel="self"' in feed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
