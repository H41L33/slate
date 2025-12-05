import sys
from pathlib import Path

import pytest

from slate import main as slate_main


def run_main_with_args(args: list[str]):
    """Helper to run slate main with args."""
    old_argv = sys.argv[:]
    sys.argv = ["slate"] + args
    try:
        slate_main.main()
    except SystemExit as e:
        if e.code != 0:
            raise ValueError(f"CLI exited with error code {e.code}") from e
    finally:
        sys.argv = old_argv


def test_draft_build_rebuild_workflow(tmp_path):
    """Tests the full draft -> build -> rebuild workflow."""
    site_name = "workflow_site"
    site_path = tmp_path / site_name

    # 1. Draft
    run_main_with_args(["draft", str(site_path)])
    assert site_path.exists()
    assert (site_path / "content" / "index.md").exists()

    # 2. Build
    # We need to change cwd to the site path or pass it as target
    # Passing as target is cleaner for tests
    run_main_with_args(["build", str(site_path)])

    # Check default output (html)
    assert (site_path / "index.html").exists()

    # 3. Rebuild
    # Rebuild relies on slate.json in CWD.
    # So we must mock CWD or ensure slate.json is written where we expect.
    # main.py writes slate.json to CWD.
    # Let's temporarily change CWD to tmp_path
    import os

    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        # Run build again to generate slate.json in tmp_path
        run_main_with_args(["build", str(site_path)])
        assert Path("slate.json").exists()

        # Delete output
        (site_path / "index.html").unlink()

        # Run rebuild
        run_main_with_args(["rebuild"])
        assert (site_path / "index.html").exists()
    finally:
        os.chdir(old_cwd)


def test_invalid_frontmatter(tmp_path):
    """Tests handling of invalid frontmatter."""
    md_file = tmp_path / "bad_fm.md"
    md_file.write_text("---\ntitle: : bad yaml\n---\n# Content", encoding="utf-8")

    # Should exit with error (SystemExit 1) or handle gracefully
    # main.py calls sys.exit(1) on validation error
    with pytest.raises(ValueError, match="CLI exited with error code 1"):
        run_main_with_args(["build", str(md_file), "--template", "t.html"])


def test_missing_template_html(tmp_path):
    """Tests error when HTML build is requested without template."""
    md_file = tmp_path / "no_template.md"
    md_file.write_text("# Content", encoding="utf-8")

    with pytest.raises(ValueError, match="CLI exited with error code 1"):
        run_main_with_args(["build", str(md_file), "-f", "html"])


def test_complex_gfm_features(tmp_path):
    """Tests complex GFM features like nested task lists and tables."""
    md_file = tmp_path / "complex.md"
    import textwrap

    content = textwrap.dedent("""
    # Complex

    - [ ] Item 1
        - [x] Nested Item 1
        - [ ] Nested Item 2

    | Col 1 | Col 2 |
    | :--- | :--- |
    | Val 1 | Val 2 |
    """)
    md_file.write_text(content, encoding="utf-8")
    template = tmp_path / "template.html"
    template.write_text("{{ content }}", encoding="utf-8")
    output = tmp_path / "complex.html"

    run_main_with_args(
        ["build", str(md_file), "-o", str(output), "--template", str(template)]
    )

    html = output.read_text(encoding="utf-8")
    # Check for nested task list structure
    assert 'type="checkbox"' in html
    assert "Nested Item 1" in html
    # Check for table
    assert "<table" in html
    assert "Val 1" in html


def test_empty_site_build(tmp_path):
    """Tests building an empty directory."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    # Should fail as no index.md found or similar error
    with pytest.raises(ValueError, match="CLI exited with error code 1"):
        run_main_with_args(["build", str(empty_dir)])


def test_multi_format_output_structure(tmp_path):
    """Tests output structure when multiple formats are requested."""
    md_file = tmp_path / "multi.md"
    md_file.write_text("# Multi", encoding="utf-8")
    template = tmp_path / "template.html"
    template.write_text("{{ content }}", encoding="utf-8")
    output_dir = tmp_path / "out_multi"

    run_main_with_args(
        [
            "build",
            str(md_file),
            "-o",
            str(output_dir),
            "--template",
            str(template),
            "--formats",
            "html,gemini,gopher",
        ]
    )

    # Should create subdirectories
    assert (output_dir / "html" / "multi.html").exists()
    assert (output_dir / "gemini" / "multi.gmi").exists()
    assert (output_dir / "gopher" / "multi.txt").exists()
