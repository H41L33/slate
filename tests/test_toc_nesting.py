from slate.parse import generate_toc


def test_toc_nesting():
    blocks = [
        {"h1": "Title 1"},
        {"h2": "Subtitle 1.1"},
        {"h3": "Section 1.1.1"},
        {"h2": "Subtitle 1.2"},
        {"h1": "Title 2"},
    ]

    toc_html = generate_toc(blocks)

    print(toc_html)

    # Current behavior: Flat list with classes
    # Expected behavior (after upgrade): Nested <ul>

    # Let's assert the nested structure we WANT.
    # If this fails, it confirms we need to implement it.

    expected_snippet = "<ul>"

    # We expect some nesting.
    # e.g.
    # <li><a...>Title 1</a>
    #   <ul>
    #     <li><a...>Subtitle 1.1</a>

    assert "<ul>" in toc_html

    # Check for nested lists (ul inside li or ul inside ul depending on implementation)
    # Ideally: <li>...<ul>...</ul></li>
    # But for now, let's just check if we have multiple <ul> tags which implies nesting
    # (The current implementation only has one <ul> wrapper)

    assert toc_html.count("<ul>") > 1
