"""Render block-oriented Markdown ASTs into several output formats.

This module provides three renderer classes:

- ``HTMLRenderer``: converts block dicts to HTML strings.
- ``GemtextRenderer``: produces gemtext (Gemini) text output.
- ``GopherRenderer``: emits a simple gophermap-like text representation.

Helpers and lightweight backward-compatible wrappers are provided at the
module level (`render_block`, `render_blocks`) so existing imports continue
to work.
"""

import html
import re
from typing import Any

HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6")
CALLOUTS = ("note", "warning", "danger", "success", "tip")

# Precompile commonly-used regexes to avoid repeated compilation at runtime.
IMAGE_RE = re.compile(r'!\[(?P<alt>[^\]]*)\]\((?P<src>[^\s\)]+)(?:\s+"(?P<caption>[^\"]*)")?\)')
LINK_RE = re.compile(r'\[(?P<label>[^\]]+)\]\((?P<href>[^\)]+)\)')
INLINE_CODE_RE = re.compile(r'`([^`]+)`')


def _escape(value: Any) -> str:
    """Return an HTML-escaped string for the given value.

    The renderer escapes values before inserting them into HTML output. Other
    formats (gemtext/gopher) intentionally emit raw text and therefore do not
    use HTML escaping.
    """
    return html.escape("" if value is None else str(value), quote=True)


def _img_replace(match: re.Match) -> str:
    alt = _escape(match.group("alt"))
    src = _escape(match.group("src"))
    caption = match.group("caption") or ""
    caption = _escape(caption.strip(' "'))
    fig = f'<figure class="content-figure"><img src="{src}" alt="{alt}" class="content-image"/>'
    if caption:
        fig += f'<figcaption class="caption">{caption}</figcaption>'
    fig += "</figure>"
    return fig


def _link_replace(match: re.Match) -> str:
    label = _escape(match.group("label"))
    href = _escape(match.group("href"))
    return f'<a href="{href}" class="content-link">{label}</a>'


def render_inline_links(text: str) -> str:
    """Replace inline images, links and inline code with HTML fragments.

    This is used by the HTML renderer; other renderers interpret raw text and
    therefore do not call this helper.
    """
    # Replace images first, then links, then inline code
    text = IMAGE_RE.sub(_img_replace, text)
    text = LINK_RE.sub(_link_replace, text)
    text = INLINE_CODE_RE.sub(lambda m: f'<code>{html.escape(m.group(1))}</code>', text)
    return text


class HTMLRenderer:
    """Render blocks to HTML strings."""

    def render_block(self, block: dict[str, Any]) -> str:
        for tag in HEADINGS:
            if tag in block:
                classes = f"content-{tag}"
                return f"<{tag} class='{classes}'>{_escape(block[tag])}</{tag}>"

        if "p" in block:
            content = render_inline_links(block["p"])
            return f"<p class='content-paragraph'>{content}</p>"

        if "blockquote" in block:
            content = _escape(block["blockquote"])
            return f"<blockquote class='content-blockquote'><p>{content}</p></blockquote>"

        for callout in CALLOUTS:
            key = f"callout-{callout}"
            if key in block:
                title = callout.capitalize()
                return (
                    f'<div class="callout callout-{callout}">'
                    f"<strong>{_escape(title)}</strong> {render_inline_links(block[key])}</div>"
                )

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

        if "image" in block:
            img = block.get("image") or {}
            src = _escape(img.get("src", ""))
            alt = _escape(img.get("alt", ""))
            caption = _escape(img.get("caption", ""))
            figcaption = f"<figcaption class='caption'>{caption}</figcaption>" if caption else ""
            return f'<figure class="content-figure"><img src="{src}" alt="{alt}" class="content-image"/>{figcaption}</figure>'

        if "code" in block:
            code_obj = block.get("code") or {}
            code = _escape(code_obj.get("text", ""))
            lang = _escape(code_obj.get("lang", "")) or "plaintext"
            class_attr = f' class="language-{lang}"' if lang else ""
            return f"<pre class='content-code'><code{class_attr}>{code}</code></pre>"
        if "table" in block:
            table = block.get("table") or {}
            headers = table.get("headers", [])
            rows = table.get("rows", [])
            thead = "".join(f"<th>{_escape(h)}</th>" for h in headers)
            tbody = ""
            for row in rows:
                tbody += "<tr>"
                for cell in row:
                    rendered = render_inline_links(cell)
                    tbody += f"<td>{rendered}</td>"
                tbody += "</tr>"
            return (
                "<table class='content-table'>"
                f"<thead><tr>{thead}</tr></thead>"
                f"<tbody>{tbody}</tbody></table>"
            )

        if "ul" in block:
            return self._render_list_html("ul", block["ul"]) 

        if "ol" in block:
            return self._render_list_html("ol", block["ol"]) 

        # No matching renderer for this block: return empty string
        return ""
    def _render_list_html(self, list_type: str, items: list[object]) -> str:
        tag = "ul" if list_type == "ul" else "ol"
        parts: list[str] = []
        for item in items:
            if isinstance(item, str):
                parts.append(f"<li>{render_inline_links(item)}</li>")
            elif isinstance(item, dict):
                # item may be {'p': 'text', 'ul': [...] } or nested list directly {'ul': [...]}
                content = ""
                nested_html = ""
                if "p" in item:
                    content = render_inline_links(item["p"])
                # detect nested lists
                if "ul" in item:
                    nested_html = self._render_list_html("ul", item["ul"])
                if "ol" in item:
                    nested_html = self._render_list_html("ol", item["ol"])
                if content or nested_html:
                    parts.append(f"<li>{content}{nested_html}</li>")
                else:
                    # fallback: render dict as text
                    parts.append(f"<li>{render_inline_links(str(item))}</li>")
            else:
                parts.append(f"<li>{render_inline_links(str(item))}</li>")
        return f"<{tag} class='content-list'>{''.join(parts)}</{tag}>"

    def render_blocks(self, blocks: list[dict[str, Any]]) -> str:
        return "\n".join(self.render_block(b) for b in blocks)


class GemtextRenderer:
    """Render a simple Gemtext (Gemini) textual representation."""

    def render_blocks(
        self,
        blocks: list[dict[str, Any]],
        title: str | None = None,
        description: str | None = None,
        date: str | None = None,
        time: str | None = None,
    ) -> str:
        # helper: render list items with indentation
        def _render_list(items, indent: int = 0, ordered: bool = False):
            out: list[str] = []
            for idx, item in enumerate(items, start=1):
                prefix = " " * indent
                if isinstance(item, str):
                    if ordered:
                        out.append(f"{prefix}{idx}. {item}")
                    else:
                        out.append(f"{prefix}* {item}")
                elif isinstance(item, dict):
                    # item may be {'p': 'text', 'ul': [...] } or nested list directly {'ul': [...]}
                    if "p" in item:
                        if ordered:
                            out.append(f"{prefix}{idx}. {item['p']}")
                        else:
                            out.append(f"{prefix}* {item['p']}")
                    # nested unordered
                    if "ul" in item:
                        out.extend(_render_list(item["ul"], indent=indent + 2, ordered=False))
                    if "ol" in item:
                        out.extend(_render_list(item["ol"], indent=indent + 2, ordered=True))
                else:
                    out.append(f"{prefix}* {str(item)}")
            return out

        # link extraction helper
        link_pat = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<href>[^\)]+)\)")

        lines: list[str] = []
        if title:
            lines.append(f"# {title}")
            if description:
                lines.append(description)
            # optional date/time header
            if date or time:
                dt = " ".join(x for x in (date or "", time or "") if x)
                if dt:
                    lines.append(dt)

        for block in blocks:
            if any(h in block for h in HEADINGS):
                for h in HEADINGS:
                    if h in block:
                        level = int(h[1])
                        lines.append("#" * level + " " + str(block[h]))
                        break
            elif "p" in block:
                text = str(block["p"])
                # replace link markup with label and append gemini link lines after
                links = [(m.group('label'), m.group('href')) for m in link_pat.finditer(text)]
                text = link_pat.sub(lambda m: m.group('label'), text)
                lines.append(text)
                for label, href in links:
                    lines.append(f"=> {href} {label}")
            elif "code" in block:
                code = block["code"].get("text", "")
                lines.append("```")
                lines.append(code)
                lines.append("```")
            elif "ul" in block:
                lines.extend(_render_list(block["ul"], indent=0, ordered=False))
            elif "ol" in block:
                lines.extend(_render_list(block["ol"], indent=0, ordered=True))
            elif "image" in block:
                img = block["image"] or {}
                src = img.get('src', '')
                alt = img.get('alt', '')
                lines.append(f"=> {src} {alt}")
            elif "blockquote" in block:
                lines.append(str(block["blockquote"]))

        return "\n\n".join(lines)


class GopherRenderer:
    """Render a Gophermap-like plain-text stub from blocks."""

    def render_blocks(
        self,
        blocks: list[dict[str, Any]],
        title: str | None = None,
        description: str | None = None,
        date: str | None = None,
        time: str | None = None,
        host: str = "localhost",
        port: int = 70,
    ) -> str:
        """Produce a simple, more spec-compliant gophermap.

        Each line follows the format: <type><display>\t<selector>\t<host>\t<port>
        For informational lines we use type 'i' and an empty selector.
        """
        lines: list[str] = []
        if title:
            lines.append(f"i{title}\t\t{host}\t{port}")
            if description:
                lines.append(f"i{description}\t\t{host}\t{port}")
            if date or time:
                dt = " ".join(x for x in (date or "", time or "") if x)
                if dt:
                    lines.append(f"i{dt}\t\t{host}\t{port}")

        def _render_list(items, indent: int = 0, ordered: bool = False):
            out: list[str] = []
            for idx, item in enumerate(items, start=1):
                prefix = " " * indent
                if isinstance(item, str):
                    if ordered:
                        display = f"{prefix}{idx}. {item}"
                    else:
                        display = f"{prefix}- {item}"
                    out.append(f"i{display}\t\t{host}\t{port}")
                elif isinstance(item, dict):
                    if "p" in item:
                        display = f"{prefix}- {item['p']}"
                        out.append(f"i{display}\t\t{host}\t{port}")
                    if "ul" in item:
                        out.extend(_render_list(item["ul"], indent=indent + 2, ordered=False))
                    if "ol" in item:
                        out.extend(_render_list(item["ol"], indent=indent + 2, ordered=True))
                else:
                    display = f"{prefix}- {str(item)}"
                    out.append(f"i{display}\t\t{host}\t{port}")
            return out

        for block in blocks:
            if "p" in block:
                display = str(block["p"]).replace("\t", " ")
                lines.append(f"i{display}\t\t{host}\t{port}")
            elif "h1" in block:
                display = "# " + str(block["h1"]) 
                lines.append(f"i{display}\t\t{host}\t{port}")
            elif "ul" in block:
                lines.extend(_render_list(block["ul"], indent=0, ordered=False))
            elif "ol" in block:
                lines.extend(_render_list(block["ol"], indent=0, ordered=True))
            elif "code" in block:
                code_text = block["code"].get("text", "")
                for line in code_text.splitlines():
                    lines.append(f"i{line}\t\t{host}\t{port}")

        # Use CRLF as gopher historically expects CRLF separators
        return "\r\n".join(lines) + "\r\n"


# Backwards-compatible thin wrappers
def render_block(block: dict[str, Any]) -> str:
    return HTMLRenderer().render_block(block)


def render_blocks(blocks: list[dict[str, Any]], fmt: str = "html", title: str | None = None, description: str | None = None) -> str:
    fmt = (fmt or "").lower()
    if fmt == "html":
        return HTMLRenderer().render_blocks(blocks)
    if fmt == "gemini" or fmt == "gemtext":
        return GemtextRenderer().render_blocks(blocks, title=title, description=description)
    if fmt == "gopher":
        return GopherRenderer().render_blocks(blocks, title=title, description=description)
    return "\n\n".join(str(b) for b in blocks)

