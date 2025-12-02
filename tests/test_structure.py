"""Tests for configurable directories and tree structure (v0.2.1)."""

import tempfile
from pathlib import Path

from slate.site import discover_site


class TestStructure:
    """Test site structure configurations."""
    
    def setup_method(self):
        """Create temporary directory for test sites."""
        self.temp_dir = tempfile.mkdtemp()
        self.root = Path(self.temp_dir).resolve()
        
        # Setup a standard site structure in a 'content' subdirectory
        self.source_dir = self.root / "content"
        self.source_dir.mkdir()
        
        # index.md
        (self.source_dir / "index.md").write_text("""---
categories: [blog]
title: Home
---
""")
        
        # blog.md
        (self.source_dir / "blog.md").write_text("""---
title: Blog
---
""")
        
        # blog/post1.md
        (self.source_dir / "blog").mkdir()
        (self.source_dir / "blog" / "post1.md").write_text("""---
title: Post 1
type: blog
date: 2024-12-01
---
""")

    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_discover_with_source_dir(self):
        """Test discovering site in a subdirectory."""
        site = discover_site(self.source_dir)
        
        assert site.root_path.resolve() == self.source_dir.resolve()
        assert site.index_page.title == "Home"
        assert len(site.categories) == 1
        
        # Default output path should be same as source
        assert site.index_page.output_path == self.source_dir / "index.html"

    def test_discover_with_output_dir(self):
        """Test discovering site with separate output directory."""
        output_dir = self.root / "dist"
        site = discover_site(self.source_dir, output_path=output_dir)
        
        # Output paths should be in dist/
        assert site.index_page.output_path == output_dir / "index.html"
        assert site.categories["blog"].root_page.output_path == output_dir / "blog.html"
        assert site.categories["blog"].pages[0].output_path == output_dir / "blog" / "post1.html"

    def test_discover_tree_structure(self):
        """Test discovering site with 'tree' structure."""
        output_dir = self.root / "dist"
        site = discover_site(self.source_dir, output_path=output_dir, structure="tree")
        
        # index.md -> dist/index.html
        assert site.index_page.output_path == output_dir / "index.html"
        
        # blog.md -> dist/pages/blog.html
        assert site.categories["blog"].root_page.output_path == output_dir / "pages" / "blog.html"
        
        # blog/post1.md -> dist/pages/blog/post1.html
        assert site.categories["blog"].pages[0].output_path == output_dir / "pages" / "blog" / "post1.html"

    def test_discover_flat_structure_explicit(self):
        """Test discovering site with explicit 'flat' structure."""
        output_dir = self.root / "dist"
        site = discover_site(self.source_dir, output_path=output_dir, structure="flat")
        
        # Should mirror source structure
        assert site.index_page.output_path == output_dir / "index.html"
        assert site.categories["blog"].root_page.output_path == output_dir / "blog.html"
        assert site.categories["blog"].pages[0].output_path == output_dir / "blog" / "post1.html"
