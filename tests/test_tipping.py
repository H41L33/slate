from unittest.mock import MagicMock

import pytest

from slate.render import (
    GemtextRenderer,
    GopherRenderer,
    HTMLRenderer,
    render_inline_links,
    render_inline_text,
)


@pytest.fixture
def tipping_frontmatter():
    return {
        "tipping": {
            "kofi": "hailey",
            "eth": "0x1234567890abcdef",
            "sol": "SolanaAddress123",
        }
    }


def test_html_tipping(tipping_frontmatter):
    renderer = HTMLRenderer()
    renderer.page = MagicMock()
    renderer.page.frontmatter = tipping_frontmatter

    text = "Support me: [!TIP]"
    output = render_inline_links(text, renderer=renderer)

    assert '<div class="content-tip">' in output
    assert 'href="https://ko-fi.com/hailey"' in output
    assert "<strong>ETH:</strong> 0x1234567890abcdef" in output
    assert "<strong>SOL:</strong> SolanaAddress123" in output


def test_gemtext_tipping(tipping_frontmatter):
    renderer = GemtextRenderer()
    renderer.page = MagicMock()
    renderer.page.frontmatter = tipping_frontmatter

    text = "Support me: [!TIP]"
    # GemtextRenderer uses render_inline_text
    output = render_inline_text(text, renderer=renderer)

    # Expecting multiple lines
    assert "Support:" in output
    assert "=> https://ko-fi.com/hailey Ko-fi" in output
    assert "* ETH: 0x1234567890abcdef" in output
    assert "* SOL: SolanaAddress123" in output


def test_gopher_tipping(tipping_frontmatter):
    renderer = GopherRenderer()
    renderer.page = MagicMock()
    renderer.page.frontmatter = tipping_frontmatter

    text = "Support me: [!TIP]"
    # GopherRenderer uses render_inline_text
    output = render_inline_text(text, renderer=renderer)

    # Expecting multiple lines (but render_inline_text returns \n separated string)
    assert "Support:" in output
    assert "Ko-fi: https://ko-fi.com/hailey" in output
    assert "- ETH: 0x1234567890abcdef" in output
    assert "- SOL: SolanaAddress123" in output


def test_no_tipping_frontmatter():
    renderer = HTMLRenderer()
    renderer.page = MagicMock()
    renderer.page.frontmatter = {}

    text = "Support me: [!TIP]"
    output = render_inline_links(text, renderer=renderer)

    # Should be empty or just text without replacement if regex matches but handler returns empty?
    # The handler returns "" if no tipping.
    # So "Support me: " + "" -> "Support me: "
    assert output == "Support me: "


def test_tipping_in_blocks(tipping_frontmatter):
    # Test integration with render_blocks for Gemtext
    renderer = GemtextRenderer()
    renderer.page = MagicMock()
    renderer.page.frontmatter = tipping_frontmatter

    blocks = [{"p": "Here is a tip: [!TIP]"}]
    output = renderer.render_blocks(blocks, page=renderer.page)

    assert "Here is a tip: Support:" in output
    assert "=> https://ko-fi.com/hailey Ko-fi" in output
