
import argparse
import contextlib
from unittest.mock import MagicMock, patch

import pytest

from slate.main import handle_update, main


@pytest.fixture
def mock_args():
    args = argparse.Namespace()
    args.input_file = "test_input.md"
    args.output_file = "test_output.html"
    args.template = "templates/basic.html"
    args.description = "Test Description"
    args.command = "update"
    return args

@patch("slate.main.load_markdown")
@patch("slate.main.parse_markdown_to_dicts")
@patch("slate.main.render_html")
@patch("os.path.exists")
def test_handle_update_html(mock_exists, mock_render, mock_parse, mock_load, mock_args):
    mock_exists.return_value = True
    mock_load.return_value = "# Test Title"
    mock_parse.return_value = [{"h1": "Test Title"}]
    
    # Mock main_parser
    mock_parser = MagicMock()
    
    handle_update(mock_args, mock_parser)
    
    mock_load.assert_called_with("test_input.md")
    mock_render.assert_called()
    mock_load.assert_called_with("test_input.md")
    mock_render.assert_called()
    # Verify render_html was called with args where output is set correctly
    # args passed to render_html is the second argument
    call_args = mock_render.call_args
    assert call_args[0][1].output == "test_output.html"

@patch("slate.main.load_markdown")
@patch("slate.main.parse_markdown_to_dicts")
@patch("slate.main.render_gemtext")
@patch("os.path.exists")
def test_handle_update_gemini(mock_exists, mock_render, mock_parse, mock_load, mock_args):
    mock_exists.return_value = True
    mock_args.output_file = "test_output.gmi"
    mock_load.return_value = "# Test Title"
    mock_parse.return_value = [{"h1": "Test Title"}]
    
    mock_parser = MagicMock()
    
    handle_update(mock_args, mock_parser)
    
    mock_render.assert_called()

@patch("os.path.exists")
def test_handle_update_missing_file(mock_exists, mock_args):
    mock_exists.return_value = False
    mock_parser = MagicMock()
    mock_parser.error.side_effect = SystemExit(2)
    
    with pytest.raises(SystemExit):
        handle_update(mock_args, mock_parser)
    
    mock_parser.error.assert_called()

def test_main_update_command_integration(tmp_path):
    # Integration test with mocked sys.argv
    input_file = tmp_path / "input.md"
    input_file.write_text("# Integration Test")
    
    output_file = tmp_path / "output.html"
    output_file.write_text("Old Content")
    
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_file = template_dir / "basic.html"
    template_file.write_text("<html>{{ content }}</html>")
    
    with (
        patch("sys.argv", ["slate", "update", str(input_file), str(output_file), "-T", str(template_file)]),
        contextlib.suppress(SystemExit)
    ):
        # We need to mock save_text or ensure it writes to tmp_path
        # The real main() calls handle_update which calls render_html which calls save_text
        # save_text writes to args.output.
        # So this should work and overwrite output_file.
        main()
        # main might exit on success or error, but here it shouldn't if args are correct?
        # Actually main() doesn't sys.exit(0) explicitly, but sys.exit(1) on error.
        
    assert output_file.read_text() != "Old Content"
    assert "Integration Test" in output_file.read_text()
