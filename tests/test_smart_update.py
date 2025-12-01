import os
import shutil
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from slate.main import handle_update, render_html
from slate.render import HTMLRenderer


class TestSmartUpdate(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.input_file = os.path.join(self.test_dir, "test.md")
        self.output_file = os.path.join(self.test_dir, "test.html")
        self.template_file = os.path.join(self.test_dir, "template.html")
        
        # Create dummy files
        with open(self.input_file, "w") as f:
            f.write("# Hello\n\nThis is a test.")
            
        with open(self.template_file, "w") as f:
            f.write("<html><body>{{content}}</body></html>")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_metadata_injection(self):
        # Test that render_html injects metadata
        blocks = [{"h1": "Hello"}]
        args = MagicMock()
        args.template = self.template_file
        args.output = self.output_file
        args.description = "Test"
        
        # Mock parser
        parser = MagicMock()
        
        render_html(blocks, args, "01/01/2024", "12:00", "Hello", parser, "v0.0.0", source_path=self.input_file)
        
        self.assertTrue(os.path.exists(self.output_file))
        with open(self.output_file) as f:
            content = f.read()
            self.assertIn("<!-- slate: {", content)
            # Use Path.resolve() to match what main.py writes
            expected_source = str(Path(self.input_file).resolve())
            expected_template = str(Path(self.template_file).resolve())
            self.assertIn(f'"source": "{expected_source}"', content)
            self.assertIn(f'"template": "{expected_template}"', content)

    def test_smart_update_reads_metadata(self):
        # First, generate the file with metadata
        blocks = [{"h1": "Hello"}]
        args = MagicMock()
        args.template = self.template_file
        args.output = self.output_file
        args.description = "Test"
        parser = MagicMock()
        render_html(blocks, args, "01/01/2024", "12:00", "Hello", parser, "v0.0.0", source_path=self.input_file)
        
        # Now try to update without input file
        update_args = MagicMock()
        update_args.output_file = self.output_file
        update_args.input_file = None # Simulate missing input
        update_args.template = None
        update_args.description = None
        update_args.format = "html" # Default
        
        # We need to mock load_markdown and parse_markdown_to_dicts to avoid full execution if possible,
        # but handle_update calls them. Let's just let them run since we have real files.
        
        # We need to patch sys.stdout to avoid printing
        with patch('sys.stdout', new=MagicMock()):
             handle_update(update_args, parser)
             # Verify that input_file and template were set from metadata
             # Use Path.resolve() to handle /var vs /private/var on macOS
             self.assertEqual(Path(update_args.input_file).resolve(), Path(self.input_file).resolve())
             self.assertEqual(Path(update_args.template).resolve(), Path(self.template_file).resolve())

    def test_updated_variable(self):
        # Test {{modify_date}} and {{version}}
        renderer = HTMLRenderer()
        
        current_date = "01/01/2025"
        version = "v0.1.6"
        
        blocks = [{"p": "Updated: {{modify_date}}, Version: {{version}}"}]
        
        output = renderer.render_blocks(blocks, modify_date=current_date, version=version)
        
        self.assertIn(f"Updated: {current_date}", output)
        self.assertIn(f"Version: {version}", output)

if __name__ == '__main__':
    unittest.main()
