"""Tests for frontmatter parsing and validation."""

from datetime import datetime
from typing import Any

import pytest

from slate.frontmatter import (
    extract_frontmatter,
    merge_with_cli_args,
    validate_frontmatter,
)


class TestExtractFrontmatter:
    """Test frontmatter extraction from Markdown."""

    def test_valid_frontmatter(self):
        """Test extraction of valid frontmatter."""
        md_text = """---
title: My Post
description: A great post
template: blog.html
---

# Hello World
This is content.
"""
        metadata, content = extract_frontmatter(md_text)

        assert metadata["title"] == "My Post"
        assert metadata["description"] == "A great post"
        assert metadata["template"] == "blog.html"
        assert content.strip().startswith("# Hello World")

    def test_no_frontmatter(self):
        """Test Markdown without frontmatter."""
        md_text = "# Hello World\n\nThis is content."
        metadata, content = extract_frontmatter(md_text)

        assert metadata == {}
        assert content == md_text

    def test_empty_frontmatter(self):
        """Test empty frontmatter block."""
        md_text = """---
---

# Content
"""
        metadata, content = extract_frontmatter(md_text)

        assert metadata == {}
        assert "# Content" in content

    def test_invalid_yaml(self):
        """Test invalid YAML in frontmatter."""
        md_text = """---
invalid: yaml: syntax::
---

Content
"""
        with pytest.raises(ValueError, match="Invalid frontmatter YAML"):
            extract_frontmatter(md_text)

    def test_complex_frontmatter(self):
        """Test frontmatter with various data types."""
        md_text = """---
title: Post Title
date: 2024-12-01
tags:
  - python
  - markdown
count: 42
active: true
---

Content
"""
        metadata, content = extract_frontmatter(md_text)

        assert metadata["title"] == "Post Title"
        assert metadata["date"] == datetime(2024, 12, 1).date()
        assert metadata["tags"] == ["python", "markdown"]
        assert metadata["count"] == 42
        assert metadata["active"] is True


class TestValidateFrontmatter:
    """Test frontmatter validation."""

    def test_valid_blog_post(self):
        """Test valid blog post frontmatter."""
        metadata = {"type": "blog-post", "date": "2024-12-01", "title": "My Post"}
        errors = validate_frontmatter(metadata, "test.md")
        assert errors == []

    def test_blog_missing_date(self):
        """Test blog post missing required date."""
        metadata = {"type": "blog-post", "title": "My Post"}
        errors = validate_frontmatter(metadata, "test.md")
        assert len(errors) == 1
        assert "require 'date'" in errors[0]

    def test_blog_missing_title(self):
        """Test blog post missing required title."""
        metadata = {"type": "blog-post", "date": "2024-12-01"}
        errors = validate_frontmatter(metadata, "test.md")
        assert len(errors) == 1
        assert "require 'title'" in errors[0]

    def test_invalid_date_format(self):
        """Test invalid date format."""
        metadata = {
            "type": "blog-post",
            "date": "12-01-2024",  # Wrong format
            "title": "My Post",
        }
        errors = validate_frontmatter(metadata, "test.md")
        assert len(errors) == 1
        assert "ISO format" in errors[0]

    def test_invalid_type(self):
        """Test invalid type value."""
        metadata = {
            "type": "article",  # Not "blog" or "page"
            "title": "My Post",
        }
        errors = validate_frontmatter(metadata, "test.md")
        assert len(errors) == 1
        assert "must be one of" in errors[0]

    def test_valid_page_type(self):
        """Test valid page type (no date required)."""
        metadata = {"type": "page", "title": "About"}
        errors = validate_frontmatter(metadata, "test.md")
        assert errors == []

    def test_invalid_category_type(self):
        """Test category must be string."""
        metadata = {
            "category": ["blog", "tech"]  # Should be string
        }
        errors = validate_frontmatter(metadata, "test.md")
        assert len(errors) == 1
        assert "must be a string" in errors[0]


class TestMergeWithCLIArgs:
    """Test merging frontmatter with CLI arguments."""

    def test_frontmatter_takes_precedence(self):
        """Test frontmatter overrides CLI args."""
        frontmatter = {"title": "FM Title", "description": "FM Desc"}
        cli_args = {"title": "CLI Title", "description": "CLI Desc", "format": "html"}

        merged = merge_with_cli_args(frontmatter, cli_args)

        assert merged["title"] == "FM Title"
        assert merged["description"] == "FM Desc"
        assert merged["format"] == "html"  # Preserved from CLI

    def test_cli_args_used_when_frontmatter_missing(self):
        """Test CLI args used when frontmatter doesn't have field."""
        frontmatter = {"title": "FM Title"}
        cli_args = {
            "title": "CLI Title",
            "description": "CLI Desc",
            "template": "t.html",
        }

        merged = merge_with_cli_args(frontmatter, cli_args)

        assert merged["title"] == "FM Title"
        assert merged["description"] == "CLI Desc"
        assert merged["template"] == "t.html"

    def test_empty_frontmatter(self):
        """Test empty frontmatter preserves all CLI args."""
        frontmatter: dict[str, Any] = {}
        cli_args = {"title": "CLI Title", "description": "CLI Desc"}

        merged = merge_with_cli_args(frontmatter, cli_args)

        assert merged == cli_args


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
