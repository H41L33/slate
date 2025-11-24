import sys
from pathlib import Path


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_main_with_args(args: list[str]):
    # Import inside function so module-level state is clean for tests
    from slate import main as slate_main
    # Patch sys.argv and run
    old_argv = sys.argv[:]
    sys.argv = ["slate"] + args
    try:
        slate_main.main()
    finally:
        sys.argv = old_argv


def test_html_output(tmp_path):
    md = tmp_path / "input.md"
    tpl = tmp_path / "template.html"
    out = tmp_path / "out" / "page.html"

    write_file(md, "# Title\n\nThis is a paragraph.")
    # Minimal Jinja template expecting content/title/description
    write_file(tpl, "<html><head><title>{{ title }}</title></head><body>{{ content }}</body></html>")

    run_main_with_args(["-i", str(md), "-T", str(tpl), "-o", str(out), "-f", "html"])

    assert out.exists(), f"Expected output file created at {out}"
    txt = out.read_text(encoding="utf-8")
    assert "Title" in txt
    assert "This is a paragraph." in txt


def test_gemini_output(tmp_path):
    md = tmp_path / "gmi.md"
    out = tmp_path / "page.gmi"
    write_file(md, "# Gemini\n\nA gemini paragraph.")

    run_main_with_args(["-i", str(md), "-o", str(out), "-f", "gemini"])

    assert out.exists()
    txt = out.read_text(encoding="utf-8")
    # Gemini stub uses '# Gemini' header
    assert "# Gemini" in txt
    assert "A gemini paragraph." in txt


def test_gopher_output(tmp_path):
    md = tmp_path / "gopher.md"
    out = tmp_path / "page.gph"
    write_file(md, "# Gopher\n\nA gopher paragraph.")

    run_main_with_args(["-i", str(md), "-o", str(out), "-f", "gopher"])

    assert out.exists()
    txt = out.read_text(encoding="utf-8")
    assert "Gopher" in txt
    assert "A gopher paragraph." in txt
