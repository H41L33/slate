from pathlib import Path
from unittest.mock import MagicMock
from slate.navigation import NavigationGenerator
from slate.site import Site, Page


def test_breadcrumbs_uses_index_title():
    # Setup mock site and index page
    site = MagicMock(spec=Site)
    site.categories = {}

    index_page = MagicMock(spec=Page)
    index_page.title = "Welcome"  # Custom title
    index_page.output_path = Path("/site/output/index.html")
    # Path objects are immutable, so we rely on the real Path behavior

    site.index_page = index_page

    # Generate breadcrumbs for index page
    html = NavigationGenerator.generate_breadcrumbs(None, site, current_page=index_page)

    # Expectation: Should use "Welcome", not "Home"
    assert "Welcome" in html
    assert "Home" not in html
