import sys
from pathlib import Path


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_main_with_args(args: list[str]):
    from slate import main as slate_main
    old_argv = sys.argv[:]
    sys.argv = ["slate"] + args
    try:
        slate_main.main()
    finally:
        sys.argv = old_argv


def test_multi_format_outputs(tmp_path: Path):
    md_path = tmp_path / "sample.md"
    tpl_path = tmp_path / "template.html"
    out_html = tmp_path / "out" / "page.html"
    out_gemini = tmp_path / "out" / "page.gmi"
    out_gopher = tmp_path / "out" / "page.gph"

    md = """
# Sample Title

A paragraph with `inline` code.

- item one
- item two

> A quote

```python
print("hi")
```

![Alt text](http://example.com/img.png "Caption here")
"""

    write_file(md_path, md)
    # Minimal template — render content and title
    write_file(tpl_path, "<html><head><title>{{ title }}</title></head><body>{{ content }}</body></html>")

    # HTML
    run_main_with_args(["-i", str(md_path), "-T", str(tpl_path), "-o", str(out_html), "-f", "html"])
    assert out_html.exists()
    h = out_html.read_text(encoding="utf-8")
    assert "Sample Title" in h
    assert "A paragraph with" in h
    assert "<code" in h or "<code>" in h
    assert "content-list" in h
    assert "content-blockquote" in h

    # Gemini
    run_main_with_args(["-i", str(md_path), "-o", str(out_gemini), "-f", "gemini"])
    assert out_gemini.exists()
    g = out_gemini.read_text(encoding="utf-8")
    assert "# Sample Title" in g
    assert "A paragraph with" in g
    assert "* item one" in g or "item one" in g
    assert "A quote" in g
    assert "print(\"hi\")" in g

    # Gopher
    run_main_with_args(["-i", str(md_path), "-o", str(out_gopher), "-f", "gopher"])
    assert out_gopher.exists()
    gp = out_gopher.read_text(encoding="utf-8")
    assert "Sample Title" in gp
    assert "A paragraph with" in gp
    assert "item one" in gp
    assert "print(\"hi\")" in gp
