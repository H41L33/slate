from pathlib import Path

from slate.parse import parse_markdown_to_dicts
from slate.render import GemtextRenderer, GopherRenderer, HTMLRenderer

KITCHEN_SINK_MD = """
# Heading 1

Paragraph with **bold**, *italic*, and ~~strike~~.

- [ ] Task 1
- [x] Task 2

---

> Blockquote

1. Ordered 1
2. Ordered 2

```python
print("Code")
```
"""

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"


def test_html_snapshot():
    blocks = parse_markdown_to_dicts(KITCHEN_SINK_MD)
    renderer = HTMLRenderer()
    output = renderer.render_blocks(blocks)
    expected = (SNAPSHOTS_DIR / "kitchen_sink.html").read_text().strip()
    # Normalize newlines for comparison
    assert output.strip() == expected


def test_gemtext_snapshot():
    blocks = parse_markdown_to_dicts(KITCHEN_SINK_MD)
    renderer = GemtextRenderer()
    output = renderer.render_blocks(blocks)
    expected = (SNAPSHOTS_DIR / "kitchen_sink.gmi").read_text().strip()
    assert output.strip() == expected


def test_gopher_snapshot():
    blocks = parse_markdown_to_dicts(KITCHEN_SINK_MD)
    renderer = GopherRenderer()
    output = renderer.render_blocks(blocks)
    expected = (SNAPSHOTS_DIR / "kitchen_sink.txt").read_text().strip()
    # Normalize Gopher CRLF for comparison if needed, but renderer produces CRLF
    # Let's strip and compare lines or just normalize to LF for test
    assert (
        output.replace("\r\n", "\n").strip() == expected.replace("\r\n", "\n").strip()
    )
