"""
This module provides the command-line interface (CLI) for the Slate tool,
which converts Markdown files into various static formats like HTML, Gemtext,
and Gophermap. It handles argument parsing, file loading, Markdown parsing,
rendering, and saving the output.
"""


import argparse
import importlib.metadata
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from slate.frontmatter import (
    extract_frontmatter,
    merge_with_cli_args,
    validate_frontmatter,
)
from slate.loader import load_markdown, load_template
from slate.navigation import build_navigation_context
from slate.parse import generate_toc, parse_markdown_to_dicts
from slate.render import GemtextRenderer, GopherRenderer, HTMLRenderer

if TYPE_CHECKING:
    from slate.site import Page, Site


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


def render_html(blocks, args, creation_date, creation_time, title, main_parser, version, source_path=None, modify_date=None, modify_time=None):
    """Renders and saves the HTML output.

    Args:
        blocks: Parsed Markdown blocks.
        args: Command-line arguments.
        creation_date: Creation date string.
        creation_time: Creation time string.
        title: Document title.
        main_parser: The main argparse parser object for error handling.
        source_path: The absolute path to the source markdown file (for metadata).
    """
    if not args.template:
        main_parser.error("HTML output requires a Jinja2 template via -T/--template")
    
    # source_date removed in v0.1.6
    pass

    html_renderer = HTMLRenderer()
    content_html = html_renderer.render_blocks(
        blocks, 
        title=title, 
        description=(args.description or ""), 
        creation_date=creation_date, 
        creation_time=creation_time,
        modify_date=modify_date,
        modify_time=modify_time,
        version=version
    )
    
    toc_html = generate_toc(blocks)
    
    template = load_template(args.template)
    html_result = template.render(
        content=content_html, 
        title=title, 
        description=(args.description or ""), 
        creation_date=creation_date, 
        creation_time=creation_time, 
        modify_date=modify_date, 
        modify_time=modify_time, 
        version=version,
        toc=toc_html
    )
    
    if source_path and args.template:
        abs_source = Path(source_path).resolve()
        abs_template = Path(args.template).resolve()
        metadata = {
            "source": str(abs_source),
            "template": str(abs_template),
            "creation_date": creation_date,
            "creation_time": creation_time
        }
        html_result += f"\n<!-- slate: {json.dumps(metadata)} -->"

    save_text(html_result, args.output)
    print(f"HTML output saved at: {args.output}")


def render_gemtext(blocks, args, creation_date, creation_time, title, main_parser, version, modify_date=None, modify_time=None):
    """Renders and saves the Gemtext output.

    Args:
        blocks: Parsed Markdown blocks.
        args: Command-line arguments.
        creation_date: Creation date string.
        creation_time: Creation time string.
        title: Document title.
        main_parser: The main argparse parser object for error handling.
    """
    gemtext_renderer = GemtextRenderer()
    text_result = gemtext_renderer.render_blocks(blocks, title=title, description=(args.description or ""), creation_date=creation_date, creation_time=creation_time, modify_date=modify_date, modify_time=modify_time, version=version)
    save_text(text_result, args.output)
    print(f"GEMINI output saved at: {args.output}")


def render_gopher(blocks, args, creation_date, creation_time, title, main_parser, version, modify_date=None, modify_time=None):
    """Renders and saves the Gopher output.

    Args:
        blocks: Parsed Markdown blocks.
        args: Command-line arguments.
        creation_date: Creation date string.
        creation_time: Creation time string.
        title: Document title.
        main_parser: The main argparse parser object for error handling.
    """
    gopher_renderer = GopherRenderer()
    text_result = gopher_renderer.render_blocks(blocks, title=title, description=(args.description or ""), creation_date=creation_date, creation_time=creation_time, modify_date=modify_date, modify_time=modify_time, version=version)
    save_text(text_result, args.output)
    print(f"GOPHER output saved at: {args.output}")


def handle_page_build(args, main_parser):
    """Handles the `page` subcommand (formerly `build`).

    Args:
        args: The command-line arguments for the `page` subcommand.
        main_parser: The main argparse parser object for error handling.
    """
    # Load Markdown and extract frontmatter
    md_text = load_markdown(args.input)
    frontmatter, content = extract_frontmatter(md_text)
    
    # Validate frontmatter
    errors = validate_frontmatter(frontmatter, args.input)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        main_parser.error("Frontmatter validation failed")
    
    # Merge frontmatter with CLI args (frontmatter takes precedence)
    cli_args_dict = {
        "title": args.title,
        "description": getattr(args, "description", None),
        "template": getattr(args, "template", None),
    }
    merged = merge_with_cli_args(frontmatter, cli_args_dict)
    
    # Update args with merged values
    if merged.get("title"):
        args.title = merged["title"]
    if merged.get("description"):
        args.description = merged["description"]
    if merged.get("template"):
        args.template = merged["template"]
    
    # Parse content (without frontmatter)
    blocks = parse_markdown_to_dicts(content)
    title = get_title(blocks, override=args.title)

    now = datetime.now()
    creation_date = now.strftime("%d/%m/%Y")
    creation_time = now.strftime("%H:%M")
    modify_date = creation_date
    modify_time = creation_time

    try:
        version = f"v{importlib.metadata.version('slate-md')}"
    except importlib.metadata.PackageNotFoundError:
        version = "v0.0.0"

    fmt = args.format.lower()
    if fmt == "html":
        render_html(blocks, args, creation_date, creation_time, title, main_parser, version, source_path=args.input, modify_date=modify_date, modify_time=modify_time)
    elif fmt == "gemini":
        render_gemtext(blocks, args, creation_date, creation_time, title, main_parser, version, modify_date=modify_date, modify_time=modify_time)
    elif fmt == "gopher":
        render_gopher(blocks, args, creation_date, creation_time, title, main_parser, version, modify_date=modify_date, modify_time=modify_time)
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
    creation_date = None
    creation_time = None

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
                    creation_date = metadata.get("creation_date")
                    creation_time = metadata.get("creation_time")
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
    frontmatter, content = extract_frontmatter(md_text)
    
    # Validate frontmatter
    errors = validate_frontmatter(frontmatter, args.input_file)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        main_parser.error("Frontmatter validation failed")
    
    # Merge frontmatter with CLI args (frontmatter takes precedence)
    cli_args_dict = {
        "description": getattr(args, "description", None),
        "template": args.template,  # May be from smart update or CLI
    }
    merged = merge_with_cli_args(frontmatter, cli_args_dict)
    
    # Update args with merged values  
    if merged.get("description"):
        args.description = merged["description"]
    if merged.get("template"):
        args.template = merged["template"]
    
    # Parse content (without frontmatter)
    blocks = parse_markdown_to_dicts(content)
    
    # Title from frontmatter or extracted from blocks
    title = frontmatter.get("title") or get_title(blocks)

    now = datetime.now()
    modify_date = now.strftime("%d/%m/%Y")
    modify_time = now.strftime("%H:%M")
    
    # Use creation date from metadata if available, otherwise use now (fallback)
    if not creation_date:
        creation_date = modify_date
    if not creation_time:
        creation_time = modify_time

    try:
        version = f"v{importlib.metadata.version('slate-md')}"
    except importlib.metadata.PackageNotFoundError:
        version = "v0.0.0"

    # Determine format from output filename extension
    ext = output_path.suffix.lower()

    # Let's write the logic to dispatch based on extension
    if ext in ('.html', '.htm'):
        render_html(blocks, args, creation_date, creation_time, title, main_parser, version, source_path=args.input_file, modify_date=modify_date, modify_time=modify_time)
    elif ext == '.gmi':
        render_gemtext(blocks, args, creation_date, creation_time, title, main_parser, version, modify_date=modify_date, modify_time=modify_time)
    elif ext == '.txt': # Gopher often uses .txt or no extension, but let's assume .txt or .gopher
        render_gopher(blocks, args, creation_date, creation_time, title, main_parser, version, modify_date=modify_date, modify_time=modify_time)
    else:
        print(f"Unknown output file extension '{ext}', defaulting to HTML.")
        render_html(blocks, args, creation_date, creation_time, title, main_parser, version, source_path=args.input_file, modify_date=modify_date, modify_time=modify_time)



def handle_site_build(args, main_parser):
    """Handles the `build` subcommand (formerly `rebuild`).
    
    Discovers site structure from source directory and rebuilds all pages
    with auto-generated navigation.
    """
    from slate.site import discover_site, validate_site_structure
    
    source_dir = Path(args.source).resolve()
    output_dir = Path(args.output).resolve() if args.output else source_dir
    templates_dir = Path(args.templates).resolve() if args.templates else None
    structure = args.structure
    
    print(f"Discovering site structure in {source_dir}...")
    print(f"Output directory: {output_dir}")
    if templates_dir:
        print(f"Templates directory: {templates_dir}")
    print(f"Structure: {structure}")
    
    # Nuclear option: Clean output directory if requested
    if getattr(args, 'clean', False):
        print("Cleaning output directory...")
        
        # SAFETY CHECK 1: Do not clean if output is source
        if output_dir == source_dir:
            print("WARNING: Output directory is same as source. Skipping clean to avoid deleting source files.")
            
        # SAFETY CHECK 2: Do not clean if output is current working directory
        elif output_dir.resolve() == Path.cwd().resolve():
            print("ERROR: Cannot use --clean when output directory is the current working directory ('.').")
            print("       This would delete your entire project!")
            print("       Please specify a subdirectory for output (e.g. 'slate build -o dist --clean').")
            sys.exit(1)
            
        # SAFETY CHECK 3: Do not clean if output contains critical project files
        elif (output_dir / ".git").exists() or (output_dir / "pyproject.toml").exists() or (output_dir / "src").exists():
            print(f"ERROR: Output directory '{output_dir}' appears to be a project root (contains .git, pyproject.toml, or src).")
            print("       Refusing to clean to prevent data loss.")
            sys.exit(1)
            
        else:
            # Safe to clean? Let's backup instead of delete to be sure.
            import datetime
            import shutil
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = output_dir.parent / f"{output_dir.name}_backup_{timestamp}"
            
            if output_dir.exists() and any(output_dir.iterdir()):
                print(f"Moving existing output to backup: {backup_dir}")
                try:
                    output_dir.rename(backup_dir)
                    output_dir.mkdir()
                except OSError as e:
                    print(f"Warning: Failed to move output directory: {e}")
                    print("Attempting to delete contents instead (fallback)...")
                    # Only delete if we are SURE it's not root (checks above passed)
                    for item in output_dir.iterdir():
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
            elif not output_dir.exists():
                output_dir.mkdir(parents=True)
                
            print("Output directory cleaned (backed up/recreated).")
    
    try:
        site = discover_site(source_dir, output_dir, structure)
    except (FileNotFoundError, ValueError) as e:
        main_parser.error(str(e))
    
    # Validate structure
    warnings = validate_site_structure(site)
    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
    
    print(f"Found {len(site.categories)} categories")
    
    # Get version
    try:
        version = f"v{importlib.metadata.version('slate-md')}"
    except importlib.metadata.PackageNotFoundError:
        version = "v0.0.0"
    
    # Rebuild index page
    print("\nBuilding index.html...")
    _rebuild_page(site.index_page, site, None, version, main_parser, templates_dir)
    
    # Rebuild each category
    for cat_name, category in site.categories.items():
        print(f"\nCategory: {cat_name}")
        
        # Rebuild category root page
        print(f"  Building {category.root_page.output_path.name}...")
        _rebuild_page(category.root_page, site, cat_name, version, main_parser, templates_dir)
        
        # Rebuild all pages in category
        for page in category.pages:
            # Show relative path from output root for clarity
            try:
                rel_output = page.output_path.relative_to(output_dir)
            except ValueError:
                rel_output = page.output_path
            print(f"  Building {rel_output}...")
            _rebuild_page(page, site, cat_name, version, main_parser, templates_dir)
        
        # Generate RSS feed if category has blog posts
        if category.blog_posts:
            from slate.rss import generate_rss_feed
            
            # Get site info from frontmatter or use defaults
            site_url = site.index_page.frontmatter.get("url", "https://example.com")
            site_title = site.index_page.title
            site_desc = site.index_page.frontmatter.get("description", "")
            
            feed_xml = generate_rss_feed(category, site_url, site_title, site_desc)
            
            # Write feed.xml to category directory
            # Tree: pages/category/feed.xml
            # Flat: category/feed.xml
            if structure == "tree":
                feed_path = output_dir / "pages" / cat_name / "feed.xml"
            else:
                feed_path = output_dir / cat_name / "feed.xml"
                
            feed_path.parent.mkdir(parents=True, exist_ok=True)
            feed_path.write_text(feed_xml, encoding="utf-8")
            
            print(f"  Generated feed.xml ({len(category.blog_posts)} posts)")
    
    print(f"\n✓ Site rebuild complete! Built {1 + len([p for cat in site.categories.values() for p in [cat.root_page] + cat.pages])} pages.")


def _rebuild_page(
    page: "Page",
    site: "Site",
    category_name: str | None,
    version: str,
    main_parser: argparse.ArgumentParser,
    templates_dir: Path | None = None
) -> None:
    """Helper to rebuild a single page.
    
    Args:
        page: Page object to rebuild
        site: Site object for navigation context
        category_name: Category name (or None for index)
        version: Slate version string
        main_parser: Parser for error reporting
        templates_dir: Optional directory to look for templates in
    """
    from types import SimpleNamespace
    
    # Parse frontmatter and content (already done during discovery, but stored in page)
    md_text = page.source_path.read_text(encoding='utf-8')
    from slate.frontmatter import extract_frontmatter
    frontmatter, content = extract_frontmatter(md_text)
    
    # Parse blocks
    blocks = parse_markdown_to_dicts(content)
    
    # Get title
    title = page.title
    
    # Build navigation context
    nav_context = build_navigation_context(site, category_name, page)
    
    # Get timestamps
    now = datetime.now()
    modify_date = now.strftime("%d/%m/%Y")
    modify_time = now.strftime("%H:%M")
    
    # Use creation dates from frontmatter or current time
    creation_date = str(frontmatter.get("date", modify_date)) if "date" in frontmatter else modify_date
    creation_time = modify_time
    
    # Get template from frontmatter or error
    template_path_str = frontmatter.get("template")
    if not template_path_str:
        print(f"  WARNING: No template specified for {page.source_path}, skipping HTML output")
        return
    
    # Resolve template path
    template_path = Path(template_path_str)
    if templates_dir and not template_path.is_absolute():
        # Try finding it in templates_dir
        potential_path = templates_dir / template_path
        if potential_path.exists():
            template_path = potential_path
    
    # Build args-like object for render functions
    args = SimpleNamespace(
        template=str(template_path),
        description=frontmatter.get("description", ""),
        output=str(page.output_path)
    )
    
    # Render HTML (only format supported for rebuild currently)
    html_renderer = HTMLRenderer()
    
    # Generate TOC
    toc_html = generate_toc(blocks)
    
    # Build context with navigation
    context = {
        "title": title,
        "description": args.description,
        "creation_date": creation_date,
        "creation_time": creation_time,
        "modify_date": modify_date,
        "modify_time": modify_time,
        "version": version,
        "toc": toc_html,
        **nav_context
    }
    
    # Render content
    content_html = html_renderer.render_blocks(
        blocks,
        title=title,
        description=args.description,
        creation_date=creation_date,
        creation_time=creation_time,
        modify_date=modify_date,
        modify_time=modify_time,
        version=version,
        site=site,
        page=page,
        toc=toc_html
    )
    
    # Apply navigation variables to content
    for var_name, var_value in nav_context.items():
        content_html = content_html.replace(f"{{{{{var_name}}}}}", var_value)
    
    # Load and render template
    try:
        template = load_template(args.template)
        final_html = template.render(content=content_html, **context)
    except FileNotFoundError:
        print(f"  ERROR: Template not found: {args.template}")
        return
    
    # Add metadata comment at end
    metadata = {
        "source": str(page.source_path.resolve()),
        "template": str(Path(args.template).resolve()),
        "creation_date": creation_date,
        "creation_time": creation_time
    }
    metadata_comment = f"<!-- slate: {json.dumps(metadata)} -->"
    final_html = final_html.rstrip() + "\n" + metadata_comment + "\n"
    
    # Write output
    page.output_path.parent.mkdir(parents=True, exist_ok=True)
    save_text(final_html, str(page.output_path))


def handle_rerun_last(args, main_parser):
    """Handles the `rebuild` subcommand (re-run last)."""
    last_run_file = Path(".slate_last_run")
    if not last_run_file.exists():
        main_parser.error("No previous run found. Run 'slate build' or 'slate page' first.")
    
    try:
        saved_args = json.loads(last_run_file.read_text())
        cmd_args = saved_args.get("args", [])
        print(f"Re-running: slate {' '.join(cmd_args)}")
        
        # We need to re-parse these arguments
        # But we can't just call main() because of recursion/exit issues.
        # Instead, we can parse them with a new parser or re-invoke the current one?
        # Re-invoking via sys.argv is hacky.
        # Let's just re-parse using the main_parser we have? 
        # But main_parser expects 'command' as first arg.
        
        # Actually, the cleanest way is to just call main() with the new args?
        # But main() creates a new parser.
        # Let's refactor main to accept args list.
        
        # Or, we can just use subprocess? No, that's heavy.
        
        # Let's just re-parse.
        # We need to strip the program name if present? No, parse_args takes a list.
        # saved_args["args"] should be the list of arguments (e.g. ['build', '-s', '.'])
        
        # We need to handle the case where the user runs `slate rebuild`.
        # We don't want to save `rebuild` as the last run.
        
        new_args = main_parser.parse_args(cmd_args)
        if hasattr(new_args, 'func'):
            new_args.func(new_args, main_parser)
            
    except Exception as e:
        main_parser.error(f"Failed to re-run last command: {e}")


def main(args_list=None):
    """Main entry point for the Slate command-line interface.

    This function sets up the argument parser, processes command-line arguments,
    and dispatches to the appropriate handler for the chosen subcommand.
    """
    main_parser = argparse.ArgumentParser(description="slate — Markdown to static formats (HTML/Gemini/Gopher)")
    subparsers = main_parser.add_subparsers(dest="command", required=True, help="Sub-command help")

    # Page command (formerly build)
    parser_page = subparsers.add_parser("page", help="Build a single page from a Markdown source")
    parser_page.add_argument("input", help="Input markdown file")
    parser_page.add_argument("output", help="Output path and filename (e.g. pages/post.html)")
    parser_page.add_argument("-f", "--format", dest="format", choices=("html", "gopher", "gemini"), default="html", help="Output format: html (default), gopher, gemini")
    parser_page.add_argument("-t", "--title", dest="title", help="Title override (instead of first H1 in the markdown)")
    parser_page.add_argument("-d", "--description", dest="description", help="Brief description of the page (metadata)")
    parser_page.add_argument("-T", "--template", dest="template", help="Jinja2 template path (required for HTML output)")
    parser_page.set_defaults(func=handle_page_build)

    # Update command
    parser_update = subparsers.add_parser("update", help="Update an existing file from a Markdown source")
    parser_update.add_argument("output_file", help="Existing file to update")
    parser_update.add_argument("input_file", nargs='?', help="Input markdown file (optional if metadata exists)")
    parser_update.add_argument("-T", "--template", dest="template", help="Jinja2 template path (required for HTML output)")
    parser_update.add_argument("-d", "--description", dest="description", help="Brief description of the page (metadata)")
    parser_update.set_defaults(func=handle_update) 
    
    # Build command (formerly rebuild)
    parser_build = subparsers.add_parser("build", help="Build entire site from index.md")
    parser_build.add_argument("-s", "--source", dest="source", default=".", help="Source directory containing Markdown files (default: current dir)")
    parser_build.add_argument("-o", "--output", dest="output", help="Output directory for HTML files (default: same as source)")
    parser_build.add_argument("-T", "--templates", dest="templates", help="Directory containing templates")
    parser_build.add_argument("--structure", dest="structure", choices=("flat", "tree"), default="flat", help="Output structure: flat (mirror source) or tree (professional)")
    parser_build.add_argument("--clean", action="store_true", help="Clean output directory before building")
    parser_build.set_defaults(func=handle_site_build)

    # Rebuild command (rerun last)
    parser_rebuild = subparsers.add_parser("rebuild", help="Re-run the last command with same arguments")
    parser_rebuild.set_defaults(func=handle_rerun_last)
    
    try:
        # Parse args
        args = main_parser.parse_args(args_list)
        
        # Save args if not rebuild/update? 
        # User said: "slate rebuild is a short-hand command to essentially re-run slate-build with the last used flags"
        # So we should save on 'build' and 'page'. Maybe 'update'?
        # Let's save on everything except 'rebuild'.
        if args.command != 'rebuild':
            try:
                # We need the raw arguments list to save, not the parsed namespace.
                # sys.argv[1:] gives us that.
                # If args_list was passed (e.g. from test), use that.
                raw_args = args_list if args_list is not None else sys.argv[1:]
                Path(".slate_last_run").write_text(json.dumps({"args": raw_args}))
            except Exception as e:
                print(f"Warning: Failed to save run state: {e}", file=sys.stderr)

        # Normalize args for update command to match build command expectations
        if args.command == 'update':
            args.output = args.output_file
            
        if hasattr(args, 'func'):
            args.func(args, main_parser)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()