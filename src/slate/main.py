"""
This module provides the command-line interface (CLI) for the Slate tool,
which converts Markdown files into various static formats like HTML, Gemtext,
and Gophermap. It handles argument parsing, file loading, Markdown parsing,
rendering, and saving the output.
"""


import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from slate.loader import load_markdown, load_template
from slate.parse import parse_markdown_to_dicts
from slate.render import GemtextRenderer, GopherRenderer, HTMLRenderer


def get_title(blocks, override=None):
    """Determines the title of the document.

    The title can be explicitly provided as an override. If no override is
    given, it attempts to find the first H1 or H2 heading in the parsed
    Markdown blocks to use as the title. If no heading is found, it defaults
    to "Untitled".

    Args:
        blocks: A list of parsed Markdown blocks (dictionaries).
        override: An optional string to use as the title, overriding any
                  title found in the Markdown content.

    Returns:
        A string representing the document's title.
    """
    if override:
        return override
    # Look for the first H1 or H2 heading in the document blocks to use as a title.
    for block in blocks:
        for heading_level in ("h1", "h2"):
            if heading_level in block:
                return block[heading_level]
    # If no suitable heading is found, use a default title.
    return "Untitled"


def save_text(text: str, output_path: str):
    """Saves the given text content to a specified output file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_html(blocks, args, date_str, time_str, title, main_parser, source_path=None):
    """Renders and saves the HTML output.

    Args:
        blocks: Parsed Markdown blocks.
        args: Command-line arguments.
        date_str: Formatted date string.
        time_str: Formatted time string.
        title: Document title.
        main_parser: The main argparse parser object for error handling.
        source_path: The absolute path to the source markdown file (for metadata).
    """
    if not args.template:
        main_parser.error("HTML output requires a Jinja2 template via -T/--template")
    
    source_date = None
    if source_path:
        src = Path(source_path)
        if src.exists():
            mtime = src.stat().st_mtime
            source_date = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y")

    html_renderer = HTMLRenderer()
    content_html = html_renderer.render_blocks(
        blocks, 
        title=title, 
        description=(args.description or ""), 
        date=date_str, 
        time=time_str,
        source_date=source_date
    )
    
    template = load_template(args.template)
    html_result = template.render(content=content_html, title=title, description=(args.description or ""), date=date_str, time=time_str)
    
    if source_path and args.template:
        abs_source = Path(source_path).resolve()
        abs_template = Path(args.template).resolve()
        metadata = {
            "source": str(abs_source),
            "template": str(abs_template)
        }
        html_result += f"\n<!-- slate: {json.dumps(metadata)} -->"

    save_text(html_result, args.output)
    print(f"HTML output saved at: {args.output}")


def render_gemtext(blocks, args, date_str, time_str, title, main_parser):
    """Renders and saves the Gemtext output.

    Args:
        blocks: Parsed Markdown blocks.
        args: Command-line arguments.
        date_str: Formatted date string.
        time_str: Formatted time string.
        title: Document title.
        main_parser: The main argparse parser object for error handling.
    """
    gemtext_renderer = GemtextRenderer()
    text_result = gemtext_renderer.render_blocks(blocks, title=title, description=(args.description or ""), date=date_str, time=time_str)
    save_text(text_result, args.output)
    print(f"GEMINI output saved at: {args.output}")


def render_gopher(blocks, args, date_str, time_str, title, main_parser):
    """Renders and saves the Gopher output.

    Args:
        blocks: Parsed Markdown blocks.
        args: Command-line arguments.
        date_str: Formatted date string.
        time_str: Formatted time string.
        title: Document title.
        main_parser: The main argparse parser object for error handling.
    """
    gopher_renderer = GopherRenderer()
    text_result = gopher_renderer.render_blocks(blocks, title=title, description=(args.description or ""), date=date_str, time=time_str)
    save_text(text_result, args.output)
    print(f"GOPHER output saved at: {args.output}")


def handle_build(args, main_parser):
    """Handles the `build` subcommand.

    Args:
        args: The command-line arguments for the `build` subcommand.
        main_parser: The main argparse parser object for error handling.
    """
    md_text = load_markdown(args.input)
    blocks = parse_markdown_to_dicts(md_text)
    title = get_title(blocks, override=args.title)

    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M")

    fmt = args.format.lower()
    if fmt == "html":
        render_html(blocks, args, date_str, time_str, title, main_parser, source_path=args.input)
    elif fmt == "gemini":
        render_gemtext(blocks, args, date_str, time_str, title, main_parser)
    elif fmt == "gopher":
        render_gopher(blocks, args, date_str, time_str, title, main_parser)
    else:
        # This part should not be reachable due to `choices` in argparse
        main_parser.error(f"Unsupported format: {fmt}")


def handle_update(args, main_parser):
    """Handles the `update` subcommand."""
    output_path = Path(args.output_file)
    if not output_path.exists():
        main_parser.error(f"Output file '{args.output_file}' does not exist. Use 'build' to create a new file.")

    # Set args.output for render functions
    args.output = args.output_file

    # Smart Update Logic: If input_file is missing, try to read metadata from output_file
    if not args.input_file:
        try:
            # Read the last 1024 bytes to find the metadata comment
            file_size = output_path.stat().st_size
            with output_path.open('r', encoding='utf-8') as f:
                seek_pos = max(0, file_size - 1024)
                f.seek(seek_pos)
                tail = f.read()
                
                # Look for <!-- slate: {...} -->
                match = re.search(r'<!-- slate: ({.*}) -->', tail)
                if match:
                    metadata = json.loads(match.group(1))
                    args.input_file = metadata.get("source")
                    # Only override template if not provided in args
                    if not args.template:
                        args.template = metadata.get("template")
                    print(f"Smart update: Detected source '{args.input_file}' and template '{args.template}'")
                else:
                    main_parser.error("Could not find Slate metadata in output file. Please specify input file.")
        except Exception as e:
             main_parser.error(f"Failed to read metadata from output file: {e}")

    if not args.input_file:
        main_parser.error("Input file is required (could not be determined automatically).")

    if not Path(args.input_file).exists():
        main_parser.error(f"Input file '{args.input_file}' does not exist.")

    md_text = load_markdown(args.input_file)
    blocks = parse_markdown_to_dicts(md_text)
    
    title = get_title(blocks)

    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M")

    # Determine format from output filename extension
    ext = output_path.suffix.lower()

    # Let's write the logic to dispatch based on extension
    if ext in ('.html', '.htm'):
        render_html(blocks, args, date_str, time_str, title, main_parser, source_path=args.input_file)
    elif ext == '.gmi':
        render_gemtext(blocks, args, date_str, time_str, title, main_parser)
    elif ext == '.txt': # Gopher often uses .txt or no extension, but let's assume .txt or .gopher
        render_gopher(blocks, args, date_str, time_str, title, main_parser)
    else:
        print(f"Unknown output file extension '{ext}', defaulting to HTML.")
        render_html(blocks, args, date_str, time_str, title, main_parser, source_path=args.input_file)


def main():
    """Main entry point for the Slate command-line interface.

    This function sets up the argument parser, processes command-line arguments,
    and dispatches to the appropriate handler for the chosen subcommand.
    """
    main_parser = argparse.ArgumentParser(description="slate — Markdown to static formats (HTML/Gemini/Gopher)")
    subparsers = main_parser.add_subparsers(dest="command", required=True, help="Sub-command help")

    # Build command
    parser_build = subparsers.add_parser("build", help="Build a new file from a Markdown source")
    parser_build.add_argument("input", help="Input markdown file")
    parser_build.add_argument("output", help="Output path and filename (e.g. pages/post.html)")
    parser_build.add_argument("-f", "--format", dest="format", choices=("html", "gopher", "gemini"), default="html", help="Output format: html (default), gopher, gemini")
    parser_build.add_argument("-t", "--title", dest="title", help="Title override (instead of first H1 in the markdown)")
    parser_build.add_argument("-d", "--description", dest="description", help="Brief description of the page (metadata)")
    parser_build.add_argument("-T", "--template", dest="template", help="Jinja2 template path (required for HTML output)")
    parser_build.set_defaults(func=handle_build) # Do not pass parser here, pass main_parser in actual call

    # Update command
    parser_update = subparsers.add_parser("update", help="Update an existing file from a Markdown source")
    parser_update.add_argument("output_file", help="Existing file to update")
    parser_update.add_argument("input_file", nargs='?', help="Input markdown file (optional if metadata exists)")
    parser_update.add_argument("-T", "--template", dest="template", help="Jinja2 template path (required for HTML output)")
    parser_update.add_argument("-d", "--description", dest="description", help="Brief description of the page (metadata)")
    parser_update.set_defaults(func=handle_update) 
    
    # Map 'output' to 'output_file' for render functions which expect args.output
    # We can do this by post-processing args or just ensuring render functions use a consistent attr.
    # render functions use args.output. 
    # Let's alias it in handle_update or change the arg name here.
    # Changing arg name to 'output' in parser_update is cleaner.
    # But the skeleton used 'output_file'. I will stick to 'output_file' in parser 
    # and set 'output' in handle_update.

    try:
        args = main_parser.parse_args()
        
        # Normalize args for update command to match build command expectations
        if args.command == 'update':
            args.output = args.output_file
            # args.input is expected by some? No, load_markdown takes args.input in handle_build, 
            # but handle_update calls load_markdown(args.input_file).
            # So we are good on input.
            # But render functions use args.output.
            
        if hasattr(args, 'func'):
            args.func(args, main_parser)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()