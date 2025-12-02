"""
Tests specifically designed to verify the correct parsing and rendering
of nested lists (both unordered and ordered) within Markdown documents.
This ensures that the Slate tool accurately represents complex list structures
in its internal block format and outputs them correctly in HTML.
"""


from slate.parse import parse_markdown_to_dicts
from slate.render import HTMLRenderer


def test_parse_nested_lists_structure():
    """Tests that nested lists are correctly parsed into the expected block structure.

    This test defines a Markdown string with nested unordered and ordered lists
    and asserts that `parse_markdown_to_dicts` produces a block structure
    where list items and their nested lists are accurately represented.
    """
    # Markdown input containing nested unordered and ordered lists.
    markdown_input = """
- Parent A
  - Child A1
  - Child A2
- Parent B
  1. Sub B1
     - Subsub B1a
"""
    # Parse the Markdown into a list of block dictionaries.
    blocks = parse_markdown_to_dicts(markdown_input)
    
    # Assert that there is at least one top-level list block.
    assert len(blocks) >= 1
    
    # Filter for unordered list blocks and get the first one.
    unordered_list_blocks = [block for block in blocks if 'ul' in block]
    assert unordered_list_blocks, 'Expected at least one unordered list block in the parsed output.'
    top_level_list = unordered_list_blocks[0]
    list_items = top_level_list['ul']

    # --- Verify the first top-level list item (Parent A) ---
    first_item = list_items[0]
    assert isinstance(first_item, dict), "First item should be a dictionary for structured content."
    assert first_item.get('p') == 'Parent A', "Expected 'Parent A' as the paragraph content."
    assert 'ul' in first_item, "Expected a nested unordered list within 'Parent A'."
    assert first_item['ul'] == ['Child A1', 'Child A2'], "Expected 'Child A1' and 'Child A2' as nested list items."

    # --- Verify the second top-level list item (Parent B) ---
    second_item = list_items[1]
    assert isinstance(second_item, dict), "Second item should be a dictionary for structured content."
    assert second_item.get('p') == 'Parent B', "Expected 'Parent B' as the paragraph content."
    assert 'ol' in second_item, "Expected a nested ordered list within 'Parent B'."
    
    # Verify the first item within the nested ordered list (Sub B1).
    first_ordered_list_item = second_item['ol'][0]
    assert isinstance(first_ordered_list_item, dict), "First item of nested ordered list should be a dictionary."
    assert first_ordered_list_item.get('p') == 'Sub B1', "Expected 'Sub B1' as the paragraph content."
    assert 'ul' in first_ordered_list_item, "Expected a nested unordered list within 'Sub B1'."
    assert first_ordered_list_item['ul'] == ['Subsub B1a'], "Expected 'Subsub B1a' as a nested list item."


def test_render_nested_lists_html():
    """Tests that nested lists are correctly rendered into HTML.

    This test takes a Markdown string with nested unordered lists,
    parses it, and then renders it to HTML. It asserts that the
    resulting HTML contains the expected nested `<ul>` and `<li>` tags.
    """
    # Markdown input with a simple nested unordered list.
    markdown_input = """
- Parent A
  - Child A1
  - Child A2
"""
    # Parse the Markdown into block dictionaries.
    blocks = parse_markdown_to_dicts(markdown_input)
    
    # Render the blocks into HTML using HTMLRenderer.
    html_renderer = HTMLRenderer()
    generated_html = html_renderer.render_blocks(blocks)
    
    # Assertions to check the structure and content of the generated HTML.
    # Expect a nested <ul> structure within the main <li>.
    assert '<ul class=\'content-ul\'>' in generated_html
    assert '<li>' in generated_html
    assert 'Child A1' in generated_html
    assert 'Parent A' in generated_html
