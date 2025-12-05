from slate.parse import generate_toc
from slate.render import HTMLRenderer


def test_heading_ids_match_toc():
    """Test that generated heading IDs match TOC links."""
    blocks = [
        {"h1": "My Heading"},
        {"h2": "Sub Heading"},
        {"h2": "Another Heading with Symbols!"},
    ]

    # 1. Generate TOC
    toc_html = generate_toc(blocks)

    # Verify TOC links
    assert 'href="#my-heading"' in toc_html
    assert 'href="#sub-heading"' in toc_html
    assert 'href="#another-heading-with-symbols"' in toc_html

    # 2. Render HTML
    renderer = HTMLRenderer()
    html_output = renderer.render_blocks(blocks)

    # Verify Heading IDs
    assert "<h1 id='my-heading' class='content-h1'>My Heading</h1>" in html_output
    assert "<h2 id='sub-heading' class='content-h2'>Sub Heading</h2>" in html_output
    assert (
        "<h2 id='another-heading-with-symbols' class='content-h2'>Another Heading with Symbols!</h2>"
        in html_output
    )
