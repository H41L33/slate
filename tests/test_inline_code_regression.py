from slate.render import HTMLRenderer


def test_inline_code_spacing():
    renderer = HTMLRenderer()

    # Case 1: Code at end of sentence
    block = {"p": "This is `code`."}
    html = renderer.render_block(block)

    assert '<code class="content-code">code</code>.' in html

    # Case 2: Code in middle of sentence
    block = {"p": "This `code` is inline."}
    html = renderer.render_block(block)
    assert (
        html
        == "<p class='content-paragraph'>This <code class=\"content-code\">code</code> is inline.</p>"
    )

    # Case 3: Multiple code blocks
    block = {"p": "`code1` and `code2`"}
    html = renderer.render_block(block)
    assert (
        html
        == '<p class=\'content-paragraph\'><code class="content-code">code1</code> and <code class="content-code">code2</code></p>'
    )
