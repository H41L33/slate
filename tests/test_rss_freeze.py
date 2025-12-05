from pathlib import Path
from unittest.mock import MagicMock

from slate.rss import generate_rss_feed
from slate.site import Category

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"


def test_rss_feed_snapshot():
    # Mock Category and Posts
    category = MagicMock(spec=Category)
    category.name = "blog"
    category.root_page = MagicMock()
    category.root_page.output_path.name = "blog"

    post1 = MagicMock()
    post1.title = "Post 1"
    post1.output_path = "blog/post-1.html"
    post1.frontmatter = {"description": "Description 1", "date": "2024-01-01"}

    post2 = MagicMock()
    post2.title = "Post 2"
    post2.output_path = "blog/post-2.html"
    post2.frontmatter = {"description": "Description 2", "date": "2024-01-02"}

    # RSS generator expects sorted posts
    category.blog_posts = [post2, post1]

    output = generate_rss_feed(
        category,
        site_url="https://example.com",
        site_title="My Site",
        site_description="My Blog posts from My Site",
    )

    expected = (SNAPSHOTS_DIR / "rss_feed.xml").read_text().strip()

    # Normalize newlines
    assert output.strip() == expected
