from unittest.mock import MagicMock

import pytest

from slate.main import handle_unified_build


@pytest.fixture
def ipfs_site_structure(tmp_path):
    """Creates a site structure for IPFS testing."""
    content_dir = tmp_path / "content"
    content_dir.mkdir()

    # Index page (root)
    (content_dir / "index.md").write_text(
        '---\ntitle: Home\ndate: 2025-12-05 13:14\ncategories: ["blog"]\ntemplate: base.html\n---\n# Home\n\n[Blog](blog/index.md)\n[Post 1](blog/post1.md)\n[About](about.md)',
        encoding="utf-8",
    )

    # About page (root)
    (content_dir / "about.md").write_text(
        "---\ntitle: About\ntemplate: base.html\n---\n# About\n[Home](index.md)",
        encoding="utf-8",
    )

    # Blog category root
    (content_dir / "blog.md").write_text(
        "---\ntitle: Blog\n---\n# Blog\n[Post 1](blog/post1.md)\n[Home](index.md)",
        encoding="utf-8",
    )

    # Blog category directory
    blog_dir = content_dir / "blog"
    blog_dir.mkdir()
    (blog_dir / "index.md").write_text(
        "---\ntitle: Blog\ntemplate: base.html\n---\n# Blog\n[Post 1](post1.md)\n[Home](../index.md)",
        encoding="utf-8",
    )
    (blog_dir / "post1.md").write_text(
        "---\ntitle: Post 1\ntype: blog-post\ndate: 2025-12-05 13:14\ntemplate: base.html\n---\n# Post 1\n\n[Back to Blog](index.md)\n[Home](../index.md)\n[Absolute Root](/index.md)",
        encoding="utf-8",
    )

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "base.html").write_text("{{ content }}", encoding="utf-8")

    return content_dir, templates_dir


def test_ipfs_relative_links(ipfs_site_structure, tmp_path):
    """Test that links are relative when --ipfs flag is used."""
    content_dir, templates_dir = ipfs_site_structure
    output_dir = tmp_path / "dist"

    # Mock arguments
    from argparse import Namespace

    args = Namespace()
    args.input = str(content_dir)
    args.target = str(content_dir)
    args.output = str(output_dir)
    args.template = str(templates_dir / "base.html")
    args.templates = str(templates_dir)
    args.structure = None
    args.formats = "html"
    args.ipfs = True
    args.clear = True
    args.dry_run = False
    args.no_interaction = True

    # Run build
    handle_unified_build(args, MagicMock())

    # Check output files
    # Single format output goes directly to output_dir
    html_dir = output_dir
    assert html_dir.exists()

    # Check index.html
    index_html = (html_dir / "index.html").read_text(encoding="utf-8")
    assert (
        'href="blog/index.html"' in index_html
        or 'href="./blog/index.html"' in index_html
    )
    assert 'href="about.html"' in index_html

    # Check blog/index.html
    blog_index_html = (html_dir / "blog/index.html").read_text(encoding="utf-8")
    assert 'href="post1.html"' in blog_index_html
    assert 'href="../index.html"' in blog_index_html

    # Check blog/post1.html
    post1_html = (html_dir / "blog/post1.html").read_text(encoding="utf-8")
    assert 'href="index.html"' in post1_html  # Back to Blog
    assert 'href="../index.html"' in post1_html  # Home

    # Check absolute link conversion
    # The absolute link /index.md in source should become ../../index.html (relative to blog/post1.html)
    # Wait, post1 is in blog/, so root is ../
    assert 'href="../index.html"' in post1_html


def test_ipfs_gemini_links(ipfs_site_structure, tmp_path):
    """Test that Gemini links are relative when --ipfs flag is used."""
    content_dir, templates_dir = ipfs_site_structure
    output_dir = tmp_path / "dist_gmi"

    # Mock arguments
    args = MagicMock()
    args.input = str(content_dir)
    args.target = str(content_dir)
    args.output = str(output_dir)
    args.template = str(templates_dir / "base.html")
    args.formats = "gemini"
    args.ipfs = True
    args.clear = True
    args.dry_run = False
    args.no_interaction = True

    # Run build
    handle_unified_build(args, MagicMock())

    # Check output files
    # Single format output goes directly to output_dir
    gmi_dir = output_dir
    assert gmi_dir.exists()

    # Check blog/post1.gmi
    post1_gmi = (gmi_dir / "blog/post1.gmi").read_text(encoding="utf-8")
    # Should have => ../index.gmi for Home
    assert "=> ../index.gmi" in post1_gmi
