from pathlib import Path
from unittest.mock import MagicMock
from slate.navigation import NavigationGenerator
from slate.site import Site, Page, Category


def test_blog_content_path_resolution():
    # Setup paths
    root_path = Path("/site/content")
    output_root = Path("/site/output")

    # Setup Site
    site = MagicMock(spec=Site)
    site.root_path = root_path
    site.categories = {}

    # Setup Blog Post
    post = MagicMock(spec=Page)
    post.title = "Test Post"
    post.source_path = root_path / "blog/post.md"
    post.output_path = output_root / "pages/blog/post.html"  # Tree structure output
    post.frontmatter = {"date": "2024-01-01"}
    post.is_blog_post = True

    # Setup Category
    category = MagicMock(spec=Category)
    category.blog_posts = [post]
    site.categories["blog"] = category

    # Setup Current Page (Index)
    current_page = MagicMock(spec=Page)
    current_page.output_path = output_root / "index.html"

    # Generate variables
    vars = NavigationGenerator.generate_blog_listing_variables(site, current_page)

    content_path = vars["blog_content"][0]

    # Current behavior (based on code analysis): relative path from output/index.html to output/blog/post.md
    # output/index.html parent is output/
    # output/blog/post.md relative to output/ is blog/post.md

    # User wants: /content/blog/post.md (or similar source path)
    # Let's see what we get currently.
    print(f"DEBUG: content_path={content_path}")

    # If the user wants the source path relative to project root, and assuming content/ is inside project root.
    # If site.root_path is /site/content, then relative path is blog/post.md.
    # If user wants /content/blog/post.md, maybe they want it relative to the parent of site.root_path?

    # Let's assert what we think the user wants based on "resolving to /content/blog/file.md"
    # This implies an absolute-looking path (starting with /) or relative to domain root?

    # For now, let's just assert it's NOT the output path structure if that's what they dislike.
    # They disliked: /html/pages/blog/the-ultimate-thinkpad.md (which looks like output structure)

    # User wants: /content/blog/post.md (source path relative to project root)
    # Since root_path is /site/content, we expect the path to include content/ if we go up one level.

    assert content_path == "/content/blog/post.md"
