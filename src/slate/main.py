import argparse
import os
from jinja2 import Environment, FileSystemLoader
from slate.parse import parse_markdown_to_dicts
from slate.render import render_block

def load_markdown(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        return f.read()

def load_template(template_path):
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    return env.get_template(os.path.basename(template_path))

def render_content(blocks):
    return "\n".join(render_block(block) for block in blocks)

def get_title(blocks, override=None):
    if override:
        return override
    for block in blocks:
        for k in ("h1", "h2"):
            if k in block:
                return block[k]
    return "Untitled"

def save_html(html, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

def main():
    parser = argparse.ArgumentParser(description="Markdown to HTML static page renderer.")
    parser.add_argument("markdown", help="Input markdown file")
    parser.add_argument("template", help="HTML page template file (Jinja)")
    parser.add_argument("-t", "--title", help="Title override (instead of first h1)")
    parser.add_argument("-o", "--output-dir", default=".", help="Output directory (defaults to cwd)")
    parser.add_argument("-n", "--name", default="output.html", help="Output HTML filename")
    args = parser.parse_args()

    md_text = load_markdown(args.markdown)
    blocks = parse_markdown_to_dicts(md_text)
    title = get_title(blocks, override=args.title)
    content_html = render_content(blocks)
    template = load_template(args.template)
    html_result = template.render(content=content_html, title=title)

    output_path = os.path.join(args.output_dir, args.name)
    save_html(html_result, output_path)
    print(f"Output saved at: {output_path}")

if __name__ == "__main__":
    main()
