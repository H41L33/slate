from pathlib import Path
from unittest.mock import MagicMock
from slate.navigation import NavigationGenerator
from slate.site import Site, Page


def test_breadcrumbs_on_index():
    # Setup mock site and index page
    site = MagicMock(spec=Site)
    site.categories = {}

    index_page = MagicMock(spec=Page)
    index_page.title = "Home"
    index_page.output_path = Path("/site/output/index.html")
    # Mock parent for relative path calculation - Path objects are immutable, so we rely on the real Path behavior
    # which is fine since we are using real Path objects for output_path

    site.index_page = index_page

    # Generate breadcrumbs for index page
    # page_category=None, current_page=index_page
    html = NavigationGenerator.generate_breadcrumbs(None, site, current_page=index_page)

    # Expectation: Should NOT be empty
    assert html != ""
    assert 'class="breadcrumbs"' in html
    assert "Home" in html
