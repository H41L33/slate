from slate.parse import parse_markdown_to_dicts
from slate.render import HTMLRenderer


def test_parse_nested_lists_structure():
    md = """
- Parent A
  - Child A1
  - Child A2
- Parent B
  1. Sub B1
     - Subsub B1a
"""

    blocks = parse_markdown_to_dicts(md)
    # Expect a single top-level list block
    assert len(blocks) >= 1
    ul_blocks = [b for b in blocks if 'ul' in b]
    assert ul_blocks, 'Expected at least one unordered list block'
    top = ul_blocks[0]
    items = top['ul']

    # First item should be a dict with 'p' and nested 'ul'
    first = items[0]
    assert isinstance(first, dict)
    assert first.get('p') == 'Parent A'
    assert 'ul' in first
    assert first['ul'] == ['Child A1', 'Child A2']

    # Second item should be dict with 'p' and nested 'ol'
    second = items[1]
    assert isinstance(second, dict)
    assert second.get('p') == 'Parent B'
    assert 'ol' in second
    # nested ordered list should contain a dict item with 'p' == 'Sub B1' and nested 'ul'
    first_ol_item = second['ol'][0]
    assert isinstance(first_ol_item, dict)
    assert first_ol_item.get('p') == 'Sub B1'
    assert 'ul' in first_ol_item
    assert first_ol_item['ul'] == ['Subsub B1a']


def test_render_nested_lists_html():
    md = """
- Parent A
  - Child A1
  - Child A2
"""
    blocks = parse_markdown_to_dicts(md)
    renderer = HTMLRenderer()
    html = renderer.render_blocks(blocks)
    # Expect nested <ul> inside first <li>
    assert '<ul class' in html
    assert '<li>' in html
    assert 'Child A1' in html
    assert 'Parent A' in html
