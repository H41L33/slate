import argparse
import os
from slate.parse import parse_markdown_to_dicts
from slate.render import HTMLRenderer, GopherRenderer, GemtextRenderer
from slate.loader import load_markdown, load_template


def get_title(blocks, override=None):
    if override:
        return override
    for block in blocks:
        for k in ("h1", "h2"):
            if k in block:
                return block[k]
    return "Untitled"


def save_text(text: str, output_path: str):
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    parser = argparse.ArgumentParser(description="slate — Markdown to static formats (HTML/Gemini/Gopher)")
    parser.add_argument("-i", "--input", dest="input", required=True, help="Input markdown file")
    parser.add_argument("-o", "--output", dest="output", required=True, help="Output path and filename (e.g. pages/post.html)")
    parser.add_argument("-t", "--title", dest="title", help="Title override (instead of first H1 in the markdown)")
    parser.add_argument("-d", "--description", dest="description", help="Brief description of the page (metadata)")
    parser.add_argument("-f", "--format", dest="format", choices=("html", "gopher", "gemini"), default="html", help="Output format: html (default), gopher, gemini")
    parser.add_argument("-T", "--template", dest="template", help="Jinja2 template path (required for HTML output)")

    args = parser.parse_args()

    md_text = load_markdown(args.input)
    blocks = parse_markdown_to_dicts(md_text)
    title = get_title(blocks, override=args.title)

    fmt = args.format.lower()
    if fmt == "html":
        if not args.template:
            parser.error("HTML output requires a Jinja2 template via -T/--template")
        renderer = HTMLRenderer()
        content_html = renderer.render_blocks(blocks)
        template = load_template(args.template)
        html_result = template.render(content=content_html, title=title, description=(args.description or ""))
        save_text(html_result, args.output)
        print(f"HTML output saved at: {args.output}")
    elif fmt == "gemini":
        renderer = GemtextRenderer()
        text_result = renderer.render_blocks(blocks, title=title, description=(args.description or ""))
        save_text(text_result, args.output)
        print(f"GEMINI output saved at: {args.output}")
    elif fmt == "gopher":
        renderer = GopherRenderer()
        text_result = renderer.render_blocks(blocks, title=title, description=(args.description or ""))
        save_text(text_result, args.output)
        print(f"GOPHER output saved at: {args.output}")
    else:
        parser.error(f"Unsupported format: {fmt}")


if __name__ == "__main__":
    main()
