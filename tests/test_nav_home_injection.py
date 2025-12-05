from pathlib import Path
from unittest.mock import MagicMock
from slate.navigation import NavigationGenerator
from slate.site import Site, Page, Category


def test_generate_header_nav_home_injection():
    # Setup mock site
    site = MagicMock(spec=Site)

    # Setup Index Page
    index_page = MagicMock(spec=Page)
    index_page.title = "Welcome"
    index_page.output_path = Path("/site/output/index.html")
    # index_page.output_path.parent = Path("/site/output")  # Mock parent for relpath
    site.index_page = index_page

    # Setup Categories (ordered: "projects", "blog")
    # Note: "projects" comes after "blog" alphabetically, but we want to test insertion order
    cat1 = MagicMock(spec=Category)
    cat1.root_page = MagicMock(spec=Page)
    cat1.root_page.title = "Projects"
    cat1.root_page.output_path = Path("/site/output/projects.html")

    cat2 = MagicMock(spec=Category)
    cat2.root_page = MagicMock(spec=Page)
    cat2.root_page.title = "Blog"
    cat2.root_page.output_path = Path("/site/output/blog.html")

    # Use a real dict to preserve insertion order
    site.categories = {"projects": cat1, "blog": cat2}

    # Generate Nav
    # current_page is index_page
    html = NavigationGenerator.generate_header_nav(site, current_page=index_page)

    # Check for Home link
    assert 'href="index.html"' in html
    assert ">Welcome</a>" in html

    # Check for Category links
    assert 'href="projects.html"' in html
    assert ">Projects</a>" in html
    assert 'href="blog.html"' in html
    assert ">Blog</a>" in html

    # Check Order: Welcome -> Projects -> Blog
    welcome_idx = html.find(">Welcome</a>")
    projects_idx = html.find(">Projects</a>")
    blog_idx = html.find(">Blog</a>")

    assert welcome_idx != -1
    assert projects_idx != -1
    assert blog_idx != -1

    assert welcome_idx < projects_idx
    assert projects_idx < blog_idx
