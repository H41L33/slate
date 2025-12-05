from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from slate.navigation import NavigationGenerator
from slate.site import Category, Page, Site


@pytest.fixture
def mock_site():
    """Create a mock site with blog posts."""
    site = MagicMock(spec=Site)
    site.categories = {}

    # Create blog category
    blog_cat = MagicMock(spec=Category)
    blog_cat.name = "blog"

    # Create blog posts with different dates
    post1 = MagicMock(spec=Page)
    post1.title = "Newest Post"
    post1.frontmatter = {
        "date": date(2025, 1, 1),
        "description": "Desc 1",
        "type": "blog-post",
    }
    post1.output_path = Path("/site/output/blog/post1.html")
    post1.is_blog_post = True

    post2 = MagicMock(spec=Page)
    post2.title = "Oldest Post"
    post2.frontmatter = {
        "date": date(2024, 1, 1),
        "description": "Desc 2",
        "type": "blog-post",
    }
    post2.output_path = Path("/site/output/blog/post2.html")
    post2.is_blog_post = True

    # Mock category.blog_posts to return sorted list (Site logic usually does this)
    blog_cat.blog_posts = [post1, post2]

    site.categories["blog"] = blog_cat
    return site


def test_generate_blog_listing_variables_html(mock_site):
    """Test generating variables for HTML format."""
    current_page = MagicMock(spec=Page)
    current_page.output_path = Path("/site/output/index.html")

    vars = NavigationGenerator.generate_blog_listing_variables(
        mock_site, current_page, fmt="html"
    )

    # Check keys
    assert "blog_title" in vars
    assert "blog_description" in vars
    assert "blog_view" in vars
    assert "blog_content" in vars

    # Check values and sorting (newest first)
    assert vars["blog_title"] == ["Newest Post", "Oldest Post"]
    assert vars["blog_description"] == ["Desc 1", "Desc 2"]

    # Check HTML links (relative to index.html)
    assert vars["blog_view"] == ["blog/post1.html", "blog/post2.html"]
    assert vars["blog_content"] == ["blog/post1.md", "blog/post2.md"]


def test_generate_blog_listing_variables_gemini(mock_site):
    """Test generating variables for Gemtext format."""
    current_page = MagicMock(spec=Page)
    current_page.output_path = Path("/site/output/index.gmi")

    vars = NavigationGenerator.generate_blog_listing_variables(
        mock_site, current_page, fmt="gemini"
    )

    # Check Gemtext links (.gmi extension)
    assert vars["blog_view"] == ["blog/post1.gmi", "blog/post2.gmi"]
    # Content links should still be .md
    assert vars["blog_content"] == ["blog/post1.md", "blog/post2.md"]


def test_generate_blog_listing_variables_gopher(mock_site):
    """Test generating variables for Gopher format."""
    current_page = MagicMock(spec=Page)
    current_page.output_path = Path("/site/output/index.txt")

    vars = NavigationGenerator.generate_blog_listing_variables(
        mock_site, current_page, fmt="gopher"
    )

    # Check Gopher links (.txt extension)
    assert vars["blog_view"] == ["blog/post1.txt", "blog/post2.txt"]
    assert vars["blog_content"] == ["blog/post1.md", "blog/post2.md"]


def test_list_synchronization(mock_site):
    """Ensure all lists have same length and order."""
    vars = NavigationGenerator.generate_blog_listing_variables(mock_site)

    length = len(vars["blog_title"])
    assert len(vars["blog_description"]) == length
    assert len(vars["blog_view"]) == length
    assert len(vars["blog_content"]) == length

    # Verify index 0 corresponds to same post across all lists
    assert vars["blog_title"][0] == "Newest Post"
    assert vars["blog_description"][0] == "Desc 1"
    assert "post1" in vars["blog_view"][0]
    assert "post1" in vars["blog_content"][0]


def test_empty_site():
    """Test behavior with no blog posts."""
    site = MagicMock(spec=Site)
    site.categories = {}

    vars = NavigationGenerator.generate_blog_listing_variables(site)

    assert vars["blog_title"] == []
    assert vars["blog_description"] == []
    assert vars["blog_view"] == []
    assert vars["blog_content"] == []
