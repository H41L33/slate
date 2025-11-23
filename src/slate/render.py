"""Render simple block structures into HTML with mapped CSS classes."""

from typing import Any, Dict
import html
import re

HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6")
CALLOUTS = ("note", "warning", "danger", "success", "tip")

def _escape(value: Any) -> str:
    """Safely convert a value to an HTML-escaped string."""
    return html.escape("" if value is None else str(value), quote=True)

def img_replace(match):
    alt = _escape(match.group('alt'))
    src = _escape(match.group('src'))
    caption = match.group('caption') or ''
    caption = _escape(caption.strip(' "'))
    fig = f'<figure class="content-figure"><img src="{src}" alt="{alt}" class="content-image"/>'
    if caption:
        fig += f'<figcaption class="caption">{caption}</figcaption>'
    fig += '</figure>'
    return fig

def link_replace(match):
    label = _escape(match.group('label'))
    href = _escape(match.group('href'))
    return f'<a href="{href}" class="content-link">{label}</a>'

def render_inline_links(text):
    # Replace images, then links, then inline code
    image_pat = r'!\[(?P<alt>[^\]]*)\]\((?P<src>[^\s\)]+)(?:\s+"(?P<caption>[^"]*)")?\)'
    text = re.sub(image_pat, img_replace, text)
    link_pat = r'\[(?P<label>[^\]]+)\]\((?P<href>[^\)]+)\)'
    text = re.sub(link_pat, link_replace, text)
    # Escape code within backticks
    text = re.sub(r'`([^`]+)`', lambda m: f'<code>{html.escape(m.group(1))}</code>', text)
    return text

def render_block(block: Dict[str, Any]) -> str:
    """Render a single block (dict) to an HTML string."""

    # Headings
    for tag in HEADINGS:
        if tag in block:
            # All headings use class for font and margin size
            classes = f"content-{tag}"
            return f"<{tag} class='{classes}'>{_escape(block[tag])}</{tag}>"

    # Paragraph
    if "p" in block:
        content = render_inline_links(block["p"])
        return f"<p class='content-paragraph'>{content}</p>"

    # Blockquote
    if "blockquote" in block:
        content = _escape(block["blockquote"])
        return f"<blockquote class='content-blockquote'><p>{content}</p></blockquote>"

    # Callout blocks
    for callout in CALLOUTS:
        key = f"callout-{callout}"
        if key in block:
            title = callout.capitalize()
            return (
                f'<div class="callout callout-{callout}">'
                f"<strong>{_escape(title)}</strong> {render_inline_links(block[key])}</div>"
            )

    # Fallback for paragraphs starting with !NOTE/!WARNING etc (if parser misses it)
    if "p" in block and block["p"].strip().startswith("!"):
        p = block["p"].strip()
        for callout in CALLOUTS:
            marker = f"!{callout.upper()}"
            if p.startswith(marker):
                content = p[len(marker):].strip()
                title = callout.capitalize()
                return (
                    f'<div class="callout callout-{callout}">'
                    f"<strong>{_escape(title)}</strong> {render_inline_links(content)}</div>"
                )

    # Image block (if parser emits structured image block)
    if "image" in block:
        img = block["image"] or {}
        src = _escape(img.get("src", ""))
        alt = _escape(img.get("alt", ""))
        caption = _escape(img.get("caption", ""))
        figcaption = f"<figcaption class='caption'>{caption}</figcaption>" if caption else ""
        return f'<figure class="content-figure"><img src="{src}" alt="{alt}" class="content-image"/>{figcaption}</figure>'

    # Code block
    if "code" in block:
        code_obj = block["code"] or {}
        code = _escape(code_obj.get("text", ""))
        lang = _escape(code_obj.get("lang", "")) or "plaintext"
        class_attr = f' class="language-{lang}"' if lang else ""
        # Wrap pre/code for codeblocks
        return f"<pre class='content-code'><code{class_attr}>{code}</code></pre>"

    # Unordered list
    if "ul" in block:
        items = "".join(f"<li>{render_inline_links(item)}</li>" for item in block["ul"]) 
        return f"<ul class='content-list'>{items}</ul>"

    # Ordered list
    if "ol" in block:
        items = "".join(f"<li>{render_inline_links(item)}</li>" for item in block["ol"]) 
        return f"<ol class='content-list'>{items}</ol>"

    # Table
    if "table" in block:
        table = block["table"] or {}
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        thead = "".join(f"<th>{_escape(h)}</th>" for h in headers)
        tbody = ""
        for row in rows:
            tbody += "<tr>"
            for cell in row:
                # If you expect code or tags, escape them!
                rendered = render_inline_links(cell)
                # If your Markdown ever puts actual HTML tags in the cell, escape again:
                # rendered = _escape(rendered)
                tbody += f"<td>{rendered}</td>"
            tbody += "</tr>"
        return (
            "<table class='content-table'>"
            f"<thead><tr>{thead}</tr></thead>"
            f"<tbody>{tbody}</tbody></table>"
        )

    return ""
