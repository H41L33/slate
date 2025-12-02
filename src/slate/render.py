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
from collections.abc import Callable
from typing import Any

HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6") # HTML heading tags supported
CALLOUTS = ("note", "warning", "danger", "success", "tip") # Types of callout blocks supported


HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6") # HTML heading tags supported
CALLOUTS = ("note", "warning", "danger", "success", "tip") # Types of callout blocks supported


# Precompile commonly-used regexes to avoid repeated compilation at runtime.
# Regex for matching Markdown image syntax: ![alt text](src "caption")
IMAGE_RE = re.compile(r'!\[(?P<alt>[^\]]*)\]\((?P<src>[^\s\)]+)(?:\s+"(?P<caption>[^\"]*)")?\)')
# Regex for matching Markdown link syntax: [label](href)
LINK_RE = re.compile(r'\[(?P<label>[^\]]+)\]\((?P<href>[^\)]+)\)')
# Regex for matching generic custom token syntax: [!TOKEN] [label](href)
CUSTOM_TOKEN_RE = re.compile(r'\[!(?P<token>[A-Z0-9-_]+)\]\s*\[(?P<label>[^\]]+)\]\((?P<href>[^\)]+)\)')
# Regex for matching inline code: `code`
INLINE_CODE_RE = re.compile(r'`([^`]+)`')


def _escape(value: Any) -> str:
    """Return an HTML-escaped string for the given value.

    The renderer escapes values before inserting them into HTML output. Other
    formats (gemtext/gopher) intentionally emit raw text and therefore do not
    use HTML escaping.
    """

    return html.escape("" if value is None else str(value), quote=True)


def _img_replace(match: re.Match) -> str:
    """Replaces a Markdown image pattern with its corresponding HTML <figure> tag.

    This helper function is used by `render_inline_links` to convert image
    Markdown into HTML, handling alt text, source, and optional captions.

    Args:
        match: A regex match object containing groups for 'alt', 'src', and 'caption'.

    Returns:
        An HTML string representing the image within a <figure> and <figcaption> if a caption is present.
    """
    # Extract alt text, source, and caption from the regex match.
    # Escape HTML sensitive characters to prevent cross-site scripting (XSS).
    alt_text = _escape(match.group("alt"))
    image_source = _escape(match.group("src"))
    caption_raw = match.group("caption") or ""
    image_caption = _escape(caption_raw.strip(' "')) # Strip quotes and extra spaces from caption.

    # Construct the base HTML for the image figure.
    figure_html = f'<figure class="content-figure"><img src="{image_source}" alt="{alt_text}" class="content-image"/>'
    # If a caption exists, add a <figcaption> tag.
    if image_caption:
        figure_html += f'<figcaption class="caption">{image_caption}</figcaption>'
    figure_html += "</figure>"
    return figure_html


def _link_replace(match: re.Match) -> str:
    """Replaces a Markdown link pattern with its corresponding HTML <a> tag.

    This helper function is used by `render_inline_links` to convert link
    Markdown into HTML.

    Args:
        match: A regex match object containing groups for 'label' and 'href'.

    Returns:
        An HTML string representing the hyperlink.
    """
    # Extract label and href from the regex match.
    # Escape HTML sensitive characters.
    link_label = _escape(match.group("label"))
    link_href = _escape(match.group("href"))
    # Construct the HTML anchor tag.
    return f'<a href="{link_href}" class="content-link">{link_label}</a>'


    # Construct the HTML anchor tag.
    return f'<a href="{link_href}" class="content-link">{link_label}</a>'


class CustomTokenRegistry:
    """Registry for custom Markdown tokens."""
    _handlers: dict[str, Callable[[re.Match], str]] = {}

    @classmethod
    def register(cls, token_name: str, handler: Callable[[re.Match], str]) -> None:
        """Register a handler for a specific token name."""
        cls._handlers[token_name.upper()] = handler

    @classmethod
    def get_handler(cls, token_name: str) -> Callable[[re.Match], str] | None:
        """Get the handler for a specific token name."""
        return cls._handlers.get(token_name.upper())


def _md_page_link_handler(match: re.Match) -> str:
    """Handler for MD-PAGE token.
    
    Replaces a special MD-PAGE link pattern with its corresponding HTML <a> tag, converting extension.
    """
    link_label = _escape(match.group("label"))
    link_href = match.group("href")
    
    # Convert .md extension to .html
    if link_href.lower().endswith('.md'):
        link_href = link_href[:-3] + '.html'
    
    link_href = _escape(link_href)
    return f'<a href="{link_href}" class="content-link">{link_label}</a>'

# Register the default MD-PAGE handler
CustomTokenRegistry.register("MD-PAGE", _md_page_link_handler)


def _button_handler(match: re.Match) -> str:
    """Handler for BUTTON token.
    
    Replaces [!BUTTON] [Label](Link) with <button class="content-button" onclick="window.location.href='Link'">Label</button>
    """
    label = _escape(match.group("label"))
    href = _escape(match.group("href"))
    return f'<button class="content-button" onclick="window.location.href=\'{href}\'">{label}</button>'

CustomTokenRegistry.register("BUTTON", _button_handler)


def _external_link_handler(match: re.Match) -> str:
    """Handler for EXTERNAL token.
    
    Replaces [!EXTERNAL] [Label](Link) with <a href="Link" class="content-external">Label</a>
    Auto-detects protocol if missing and simplifies label if it's a URL.
    """
    label = _escape(match.group("label"))
    href = _escape(match.group("href"))
    
    # Auto-prepend protocol for specific types that are often mistaken for relative paths
    # But respect "raw" for everything else (e.g. /files/archive.zip, custom-scheme:...)
    if not re.match(r'^[a-zA-Z0-9]+://', href) and not href.startswith(('/', './', '../')):
        if href.endswith('.onion'):
            href = f"http://{href}"
        elif href.endswith('.gopher'):
            href = f"gopher://{href}"
        elif href.endswith('.gemini'):
            href = f"gemini://{href}"
        elif href.endswith('.eth'):
             href = f"https://{href}"
        elif href.startswith('www.'):
             href = f"https://{href}"
        # Otherwise leave it raw (e.g. "about.haileywelsh.me" might be intended as raw, 
        # but user asked for "www urls" to resolve. "about.haileywelsh.me" doesn't start with www.
        # If it looks like a domain? 
        # User example: "about.haileywelsh.me" -> "https://about.haileywelsh.me/index.html" (in their request text)
        # But they also said "Can WWW urls (about.haileywelsh.me) just resolve to https://example.com".
        # Let's assume if it has a TLD and no protocol, we might want https?
        # But "raw" is safer. Let's stick to the explicit list + www. 
        # If they type "google.com", it stays "google.com" (relative). 
        # If they want it absolute, they should probably type "google.com" with protocol OR we add a heuristic.
        # Given "whatever the user says goes", I'll stick to the specific extensions they complained about + www.
    
    # Simplify label: remove protocol and www for display
    clean_label = re.sub(r'^[a-zA-Z0-9]+://', '', label)
    clean_label = re.sub(r'^www\.', '', clean_label)
    
    return f'<a href="{href}" class="content-external">{clean_label}</a>'

CustomTokenRegistry.register("EXTERNAL", _external_link_handler)


def _custom_token_replace(match: re.Match) -> str:
    """Dispatcher for custom tokens."""
    token = match.group("token")
    handler = CustomTokenRegistry.get_handler(token)
    if handler:
        return handler(match)
    # If no handler found, return the original text (or handle otherwise)
    # For now, let's return the match as is, or maybe we should strip the token?
    # Returning as is seems safest if unknown.
    return match.group(0)


def render_inline_links(text: str, site: Any = None, current_page: Any = None) -> str:
    """Replaces inline Markdown images, links, and code with their HTML equivalents.

    Args:
        text: The input text string.
        site: Optional Site object for resolving links.
        current_page: Optional Page object for relative path calculation.

    Returns:
        The text string with Markdown inline elements replaced by HTML.
    """
    # First, replace all image Markdown with HTML <figure> tags.
    text = IMAGE_RE.sub(_img_replace, text)

    # Helper for smart link resolution (used by MD-PAGE)
    def resolve_smart_link(href: str) -> str:
        if not (site and current_page):
            return href
            
        # If it's a markdown file, try to resolve it
        if href.endswith(".md"):
            # Try to find the target page in the site
            # href is relative to current page source OR absolute from site root
            try:
                target_source = None
                if href.startswith("/"):
                     # Absolute path from site root
                     # Remove leading slash and resolve against site root
                     # We don't have site root path easily accessible here directly if not passed?
                     # Site object has root_path.
                     target_source = (site.root_path / href.lstrip("/")).resolve()
                else:
                     # Relative path
                     target_source = (current_page.source_path.parent / href).resolve()
                
                # Find page with this source path
                target_page = None
                
                # Check index
                if site.index_page.source_path.resolve() == target_source:
                    target_page = site.index_page
                
                # Check categories
                if not target_page:
                    for category in site.categories.values():
                        if category.root_page.source_path.resolve() == target_source:
                            target_page = category.root_page
                            break
                        for page in category.pages:
                            if page.source_path.resolve() == target_source:
                                target_page = page
                                break
                        if target_page:
                            break
                
                if target_page:
                    # Calculate relative path from current output to target output
                    import os
                    rel_path = os.path.relpath(target_page.output_path, current_page.output_path.parent)
                    return rel_path
                else:
                    # Fallback: just replace extension
                    return href[:-3] + ".html"
            except Exception:
                # If resolution fails, fallback to simple replacement
                return href[:-3] + ".html"
        return href

    # Custom token replacer that handles MD-PAGE specifically with context
    def custom_token_replacer_with_context(match: re.Match) -> str:
        token = match.group("token")
        if token == "MD-PAGE":
            # Handle MD-PAGE with smart resolution
            label = _escape(match.group("label"))
            href = match.group("href")
            
            # Apply smart resolution
            resolved_href = resolve_smart_link(href)
            
            # Ensure extension is .html if it was .md (resolve_smart_link handles this usually, but double check)
            if resolved_href.lower().endswith(".md"):
                 resolved_href = resolved_href[:-3] + ".html"
            
            return f'<a href="{_escape(resolved_href)}" class="content-md_page">{label}</a>'
        else:
            # Delegate to registry for other tokens
            return _custom_token_replace(match)

    # Replace custom tokens using the context-aware replacer
    text = CUSTOM_TOKEN_RE.sub(custom_token_replacer_with_context, text)
    
    # Replace links with SIMPLE replacement (no smart resolution for standard links)
    def link_replacer(match: re.Match) -> str:
        label = _escape(match.group("label"))
        href = match.group("href")
        
        # If it's an external link or anchor, leave it alone
        if href.startswith(("http://", "https://", "#", "mailto:")):
            return f'<a href="{_escape(href)}" class="content-link">{label}</a>'
            
        # Simple extension replacement for .md files
        if href.lower().endswith(".md"):
             href = href[:-3] + ".html"
             
        return f'<a href="{_escape(href)}" class="content-link">{label}</a>'

    text = LINK_RE.sub(link_replacer, text)
    
    # Finally, replace all inline code (backticks) with HTML <code> tags.
    text = INLINE_CODE_RE.sub(lambda m: f'<code class="content-code">{html.escape(m.group(1))}</code>', text)
    return text


class VariableRegistry:
    """Registry for template variables."""
    _handlers: dict[str, Callable[[dict[str, Any]], str]] = {}

    @classmethod
    def register(cls, name: str, handler: Callable[[dict[str, Any]], str]):
        """Register a handler for a variable name."""
        cls._handlers[name] = handler

    @classmethod
    def get_value(cls, name: str, context: dict[str, Any]) -> str:
        """Get the value of a variable given the context."""
        handler = cls._handlers.get(name)
        if handler:
            return handler(context)
        return ""

# Register default variables
VariableRegistry.register("creation_date", lambda c: c.get("creation_date", ""))
VariableRegistry.register("creation_time", lambda c: c.get("creation_time", ""))
VariableRegistry.register("modify_date", lambda c: c.get("modify_date", ""))
VariableRegistry.register("modify_time", lambda c: c.get("modify_time", ""))
VariableRegistry.register("version", lambda c: c.get("version", ""))
VariableRegistry.register("datetime", lambda c: " ".join(x for x in (c.get("creation_date", ""), c.get("creation_time", "")) if x))

# Navigation variables (v0.2.0)
VariableRegistry.register("nav_header", lambda c: c.get("nav_header", ""))
VariableRegistry.register("nav_category", lambda c: c.get("nav_category", ""))
VariableRegistry.register("category_name", lambda c: c.get("category_name", ""))
VariableRegistry.register("breadcrumbs", lambda c: c.get("breadcrumbs", ""))

# Content enhancement variables (v0.2.0)
VariableRegistry.register("toc", lambda c: c.get("toc", ""))


class BaseRenderer:
    """Base class for all renderers."""
    
    def __init__(self):
        self.title: str | None = None
        self.description: str | None = None
        self.creation_date: str | None = None
        self.creation_time: str | None = None
        self.modify_date: str | None = None
        self.modify_time: str | None = None
        self.version: str | None = None
        self.site: Any = None
        self.page: Any = None
        self.toc: str | None = None

    def _apply_dt(self, s: str | None) -> str:
        """Applies variable placeholders to a string using the VariableRegistry."""
        if s is None:
            return ""
        
        context = {
            "title": self.title,
            "description": self.description,
            "creation_date": self.creation_date,
            "creation_time": self.creation_time,
            "modify_date": self.modify_date,
            "modify_time": self.modify_time,
            "version": self.version,
            "toc": self.toc
        }
        # We need to find all {{variable}} patterns and replace them
        # A simple regex for {{name}}
        return re.sub(r'\{\{([a-zA-Z0-9-_]+)\}\}', lambda m: VariableRegistry.get_value(m.group(1), context), s)

    def render_blocks(
        self,
        blocks: list[dict[str, Any]],
        title: str | None = None,
        description: str | None = None,
        creation_date: str | None = None,
        creation_time: str | None = None,
        modify_date: str | None = None,
        modify_time: str | None = None,
        version: str | None = None,
        site: Any = None,
        page: Any = None,
        toc: str | None = None,
        **kwargs
    ) -> str:
        """Renders a list of blocks. Subclasses must implement specific logic."""
        self.title = title
        self.description = description
        self.creation_date = creation_date
        self.creation_time = creation_time
        self.modify_date = modify_date
        self.modify_time = modify_time
        self.version = version
        self.site = site
        self.page = page
        self.toc = toc
        return ""


class HTMLRenderer(BaseRenderer):
    """Renders a list of Markdown block dictionaries into an HTML string.

    This renderer converts the structured block data generated by the parser
    into standard HTML tags, applying appropriate styling classes and handling
    various Markdown elements suchs as headings, paragraphs, lists, code blocks,
    images, blockquotes, callouts, and tables. It also supports dynamic
    replacement of `{{date}}` and `{{time}}` placeholders within the content.
    """

    def render_block(self, block: dict[str, Any]) -> str:
        """Renders a single Markdown block dictionary into its HTML string representation."""

        # Render Headings (h1, h2, etc.)
        for tag_name in HEADINGS:
            if tag_name in block:
                # Construct HTML class for styling (e.g., 'content-h1').
                css_classes = f"content-{tag_name}"
                # Escape content and replace date/time placeholders.
                content = _escape(self._apply_dt(block[tag_name]))
                return f"<{tag_name} class='{css_classes}'>{content}</{tag_name}>"


        # Render Paragraphs
        if "p" in block:
            # Escape content, replace date/time placeholders, and handle inline links/images.
            processed_content = render_inline_links(
                self._apply_dt(block["p"]),
                site=self.site,
                current_page=self.page
            )
            return f"<p class='content-paragraph'>{processed_content}</p>"


        # Render Blockquotes
        if "blockquote" in block:
            # Escape content and replace date/time placeholders.
            blockquote_content = _escape(self._apply_dt(block["blockquote"]))
            return f"<blockquote class='content-blockquote'><p>{blockquote_content}</p></blockquote>"


        # Render Callouts (e.g., [!NOTE], [!WARNING])
        for callout_type in CALLOUTS:
            block_key = f"callout-{callout_type}"
            if block_key in block:
                # Capitalize the callout type for display (e.g., "Note", "Warning").
                display_title = callout_type.capitalize()
                # Escape display title, replace date/time placeholders in content,
                # and handle inline links/images within callout text.
                callout_content = render_inline_links(
                    self._apply_dt(block[block_key]),
                    site=self.site,
                    current_page=self.page
                )
                return (
                    f'<div class="content-callout callout callout-{callout_type}">'
                    f"<strong>{_escape(display_title)}</strong> {callout_content}</div>"
                )


        # Alternative Callout Parsing (if paragraph starts with !TYPE)
        # This block appears to be a fallback or alternative parsing method for callouts
        # that might be redundant with the block above if parsing is consistent.
        # It checks if a paragraph starts with a marker like "!NOTE".
        if "p" in block and block["p"].strip().startswith("!"):
            paragraph_text = block["p"].strip()
            for callout_type in CALLOUTS:
                marker_upper = f"!{callout_type.upper()}"
                if paragraph_text.startswith(marker_upper):
                    # Extract content after the marker.
                    extracted_content = paragraph_text[len(marker_upper):].strip()
                    display_title = callout_type.capitalize()
                    callout_content = render_inline_links(
                        self._apply_dt(extracted_content),
                        site=self.site,
                        current_page=self.page
                    )
                    return (
                        f'<div class="content-callout callout-{callout_type}">'
                        f"<strong>{_escape(display_title)}</strong> {callout_content}</div>"
                    )


        # Render Images
        if "image" in block:
            image_data = block.get("image") or {}
            # Extract and escape image attributes. Replace date/time in alt and caption.
            source_url = _escape(image_data.get("src", ""))
            alt_text = _escape(self._apply_dt(image_data.get("alt", "")))
            image_caption = _escape(self._apply_dt(image_data.get("caption", "")))
            
            # Create figcaption HTML only if a caption is provided.
            figcaption_html = f"<figcaption class='caption'>{image_caption}</figcaption>" if image_caption else ""
            return (
                f'<figure class="content-figure">'
                f'<img src="{source_url}" alt="{alt_text}" class="content-image"/>'
                f'{figcaption_html}</figure>'
            )


        # Render Code Blocks
        if "code" in block:
            code_data = block.get("code") or {}
            # Extract and escape code content and language.
            code_text = _escape(code_data.get("text", ""))
            code_language = _escape(code_data.get("lang", "")) or "plaintext"
            # Add language class for syntax highlighting if specified.
            language_class_attr = f' class="language-{code_language}"' if code_language else ""
            return f"<pre class='content-code'><code{language_class_attr}>{code_text}</code></pre>"
        
        # Render Tables
        if "table" in block:
            table_data = block.get("table") or {}
            table_headers = table_data.get("headers", [])
            table_rows = table_data.get("rows", [])
            
            # Render table headers. Replace date/time in header text.
            header_html = "".join(f"<th>{_escape(self._apply_dt(h))}</th>" for h in table_headers)
            
            # Render table body rows and cells. Replace date/time and inline links in cell content.
            body_html = ""
            for row_data in table_rows:
                body_html += "<tr>"
                for cell_content in row_data:
                    rendered_cell = render_inline_links(
                        self._apply_dt(cell_content),
                        site=self.site,
                        current_page=self.page
                    )
                    body_html += f"<td>{rendered_cell}</td>"
                body_html += "</tr>"
            
            return (
                "<table class='content-table'>"
                f"<thead><tr>{header_html}</tr></thead>"
                f"<tbody>{body_html}</tbody></table>"
            )


        # Render Unordered Lists
        if "ul" in block:
            return self._render_list_html("ul", block["ul"]) 


        if "ol" in block:
            return self._render_list_html("ol", block["ol"]) 

        # No matching renderer for this block: return empty string
        return ""
    def _render_list_html(self, list_type: str, items: list[object]) -> str:
        """Helper method to recursively render an HTML list (unordered or ordered).

        This function processes a list of items, where each item can be a string,
        a dictionary (for items with paragraphs and/or nested lists), or other
        objects. It recursively calls itself to render nested lists.

        Args:
            list_type: A string, either "ul" for unordered list or "ol" for ordered list.
            items: A list of items to be rendered within the list. Each item can be
                   a string (plain text), a dictionary (for structured content),
                   or another object.

        Returns:
            An HTML string representing the fully rendered list, including its items
            and any nested lists.
        """
        # Determine the HTML tag for the list (<ul> or <ol>).
        list_html_tag = "ul" if list_type == "ul" else "ol"
        
        # This list will accumulate the HTML strings for each list item.
        list_item_parts: list[str] = []
        
        for item_data in items:
            # Handle plain string list items.
            if isinstance(item_data, str):
                # Apply date/time placeholders, render inline links, and wrap in <li>.
                processed_content = render_inline_links(
                    self._apply_dt(item_data),
                    site=self.site,
                    current_page=self.page
                )
                list_item_parts.append(f"<li>{processed_content}</li>")
            
            # Handle dictionary list items (can contain paragraphs and/or nested lists).
            elif isinstance(item_data, dict):
                item_content_html = ""
                nested_list_html = ""
                
                # If the item has a paragraph ('p') key, process its content.
                if "p" in item_data:
                    processed_paragraph = render_inline_links(
                        self._apply_dt(item_data["p"]),
                        site=self.site,
                        current_page=self.page
                    )
                    item_content_html = processed_paragraph
                
                # Detect and recursively render nested unordered lists.
                if "ul" in item_data:
                    nested_list_html = self._render_list_html("ul", item_data["ul"])
                # Detect and recursively render nested ordered lists.
                if "ol" in item_data:
                    nested_list_html = self._render_list_html("ol", item_data["ol"])
                
                # Combine content and nested list HTML for the current list item.
                if item_content_html or nested_list_html:
                    list_item_parts.append(f"<li>{item_content_html}{nested_list_html}</li>")
                else:
                    # Fallback for dictionaries without 'p' or nested lists (e.g., malformed).
                    fallback_content = render_inline_links(
                        self._apply_dt(str(item_data)),
                        site=self.site,
                        current_page=self.page
                    )
                    list_item_parts.append(f"<li>{fallback_content}</li>")
            
            # Handle other types of list items (e.g., direct objects converted to string).
            else:
                fallback_content = render_inline_links(
                    self._apply_dt(str(item_data)),
                    site=self.site,
                    current_page=self.page
                )
                list_item_parts.append(f"<li>{fallback_content}</li>")
        
        # Join all list item HTML strings and wrap them in the appropriate list tag.
        # Join all list item HTML strings and wrap them in the appropriate list tag.
        css_class = f"content-{list_html_tag}"
        return f"<{list_html_tag} class='{css_class}'>{''.join(list_item_parts)}</{list_html_tag}>"

    def render_blocks(
        self,
        blocks: list[dict[str, Any]],
        title: str | None = None,
        description: str | None = None,
        creation_date: str | None = None,
        creation_time: str | None = None,
        modify_date: str | None = None,
        modify_time: str | None = None,
        version: str | None = None,
        site: Any = None,
        page: Any = None,
        toc: str | None = None,
        **kwargs
    ) -> str:
        """Renders a list of Markdown block dictionaries into a complete HTML string."""
        super().render_blocks(
            blocks, 
            title, 
            description, 
            creation_date, 
            creation_time, 
            modify_date=modify_date, 
            modify_time=modify_time, 
            version=version,
            site=site,
            page=page,
            toc=toc
        )
        return "\n".join(self.render_block(b) for b in blocks)


class GemtextRenderer(BaseRenderer):
    """Renders a list of Markdown block dictionaries into a Gemtext string.

    Gemtext is a minimalist markup language used for the Gemini protocol.
    This renderer converts parsed Markdown blocks into their Gemtext equivalents,
    including headings, paragraphs, lists, code blocks, and links. It also
    supports dynamic date and time placeholder replacement.
    """


    def render_blocks(
        self,
        blocks: list[dict[str, Any]],
        title: str | None = None,
        description: str | None = None,
        creation_date: str | None = None,
        creation_time: str | None = None,
        modify_date: str | None = None,
        modify_time: str | None = None,
        version: str | None = None,
        site: Any = None,
        page: Any = None,
        toc: str | None = None,
        **kwargs
    ) -> str:
        """Renders a list of Markdown block dictionaries into a complete Gemtext string."""
        super().render_blocks(
            blocks, 
            title, 
            description, 
            creation_date, 
            creation_time, 
            modify_date=modify_date, 
            modify_time=modify_time, 
            version=version,
            site=site,
            page=page,
            toc=toc,
            **kwargs
        )
        
        # Inner helper function to recursively render list items with appropriate Gemtext indentation.
        def _render_list(list_items, indent: int = 0, is_ordered: bool = False):
            output_lines: list[str] = []
            # Iterate through each item in the list.
            for item_index, item_data in enumerate(list_items, start=1):
                # Calculate the prefix for indentation.
                indent_prefix = " " * indent
                
                if isinstance(item_data, str):
                    # For a plain string item, apply the correct list marker (* for unordered, N. for ordered).
                    if is_ordered:
                        output_lines.append(f"{indent_prefix}{item_index}. {item_data}")
                    else:
                        output_lines.append(f"{indent_prefix}* {item_data}")
                
                elif isinstance(item_data, dict):
                    # If the item is a dictionary, it might contain a paragraph and/or nested lists.
                    if "p" in item_data:
                        # Apply list marker to the paragraph content.
                        if is_ordered:
                            output_lines.append(f"{indent_prefix}{item_index}. {item_data['p']}")
                        else:
                            output_lines.append(f"{indent_prefix}* {item_data['p']}")
                    
                    # Recursively render nested unordered lists.
                    if "ul" in item_data:
                        output_lines.extend(_render_list(item_data["ul"], indent=indent + 2, is_ordered=False))
                    # Recursively render nested ordered lists.
                    if "ol" in item_data:
                        output_lines.extend(_render_list(item_data["ol"], indent=indent + 2, is_ordered=True))
                else:
                    # Fallback for unexpected item types, treating them as strings.
                    output_lines.append(f"{indent_prefix}* {str(item_data)}")
            return output_lines


        # Regex to find Markdown link patterns within text for Gemtext conversion.
        link_pattern = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<href>[^\)]+)\)")


        rendered_lines: list[str] = []
        # Add title and description (if provided) as Gemtext headers.
        if title:
            rendered_lines.append(f"# {self._apply_dt(title)}") # Main title
            if description:
                rendered_lines.append(self._apply_dt(description)) # Description below title
            
            # Optionally add date/time if available.
            if creation_date or creation_time:
                combined_datetime = " ".join(x for x in (creation_date or "", creation_time or "") if x)
                if combined_datetime:
                    rendered_lines.append(combined_datetime)


        # Iterate through each parsed Markdown block to convert it to Gemtext.
        for block in blocks:
            # Render Headings (H1, H2, H3, etc.)
            if any(h_tag in block for h_tag in HEADINGS):
                for h_tag in HEADINGS:
                    if h_tag in block:
                        heading_level = int(h_tag[1]) # Extract heading level (e.g., 1 from 'h1').
                        # Gemtext headings use # based on level.
                        rendered_lines.append("#" * heading_level + " " + self._apply_dt(str(block[h_tag])))
                        break # Only process the first heading found in the block.
            
            # Render Paragraphs and Links
            elif "p" in block:
                # Apply date/time placeholders to the paragraph text.
                paragraph_text = self._apply_dt(str(block["p"]))
                
                # Extract links from the paragraph to format them for Gemtext.
                extracted_links = [(m.group('label'), m.group('href')) for m in link_pattern.finditer(paragraph_text)]
                # Remove Markdown link syntax from the paragraph text itself.
                paragraph_text = link_pattern.sub(lambda m: m.group('label'), paragraph_text)
                rendered_lines.append(paragraph_text)
                
                # Add Gemtext link lines after the paragraph.
                for link_label, link_href in extracted_links:
                    rendered_lines.append(f"=> {link_href} {link_label}")
            
            # Render Code Blocks
            elif "code" in block:
                code_content = block["code"].get("text", "")
                rendered_lines.append("```") # Gemtext code block start marker.
                rendered_lines.append(code_content)
                rendered_lines.append("```") # Gemtext code block end marker.
            
            # Render Unordered Lists
            elif "ul" in block:
                # Use the inner helper to render the list.
                rendered_lines.extend(_render_list(block["ul"], indent=0, is_ordered=False))
            
            # Render Ordered Lists
            elif "ol" in block:
                # Use the inner helper to render the list.
                rendered_lines.extend(_render_list(block["ol"], indent=0, is_ordered=True))
            
            # Render Images
            elif "image" in block:
                image_data = block["image"] or {}
                image_src = image_data.get('src', '')
                image_alt = self._apply_dt(image_data.get('alt', ''))
                # Gemtext links are used for images.
                rendered_lines.append(f"=> {image_src} {image_alt}")
            
            # Render Blockquotes
            elif "blockquote" in block:
                # Gemtext blockquotes start with '> '.
                rendered_lines.append(f"> {str(block['blockquote'])}")

        # Join all rendered lines with double newlines to separate blocks in Gemtext.
        return "\n\n".join(rendered_lines)


class GopherRenderer(BaseRenderer):
    """Renders a list of Markdown block dictionaries into a Gophermap-like plain-text format.

    Gophermap is a simple, line-oriented text format for the Gopher protocol.
    This renderer converts parsed Markdown blocks into corresponding Gophermap
    lines, which include informational lines ('i' type) and handle structured
    content like headings, paragraphs, lists, and code blocks. It also
    supports dynamic date and time placeholder replacement.
    """


    def render_blocks(
        self,
        blocks: list[dict[str, Any]],
        title: str | None = None,
        description: str | None = None,
        creation_date: str | None = None,
        creation_time: str | None = None,
        modify_date: str | None = None,
        modify_time: str | None = None,
        version: str | None = None,
        site: Any = None,
        page: Any = None,
        toc: str | None = None,
        host: str = "localhost",
        port: int = 70,
        **kwargs
    ) -> str:
        """Produces a simple, Gophermap-compliant text representation from Markdown blocks."""
        super().render_blocks(
            blocks, 
            title, 
            description, 
            creation_date, 
            creation_time, 
            modify_date=modify_date, 
            modify_time=modify_time, 
            version=version,
            site=site,
            page=page,
            toc=toc,
            **kwargs
        )


        gopher_lines: list[str] = []
        # Add title and description (if provided) as informational Gophermap lines.
        if title:
            gopher_lines.append(f"i{self._apply_dt(title)}\t\t{host}\t{port}")
            if description:
                gopher_lines.append(f"i{self._apply_dt(description)}\t\t{host}\t{port}")
            
            # Optionally add date/time if available.
            if creation_date or creation_time:
                combined_datetime = " ".join(x for x in (creation_date or "", creation_time or "") if x)
                if combined_datetime:
                    gopher_lines.append(f"i{combined_datetime}\t\t{host}\t{port}")


        # Inner helper function to recursively render list items for Gophermap.
        def _render_list(list_items, indent: int = 0, is_ordered: bool = False):
            output_lines: list[str] = []
            # Iterate through each item in the list.
            for item_index, item_data in enumerate(list_items, start=1):
                indent_prefix = " " * indent
                
                # Handle plain string list items.
                if isinstance(item_data, str):
                    display_text = ""
                    if is_ordered:
                        display_text = f"{indent_prefix}{item_index}. {self._apply_dt(item_data)}"
                    else:
                        display_text = f"{indent_prefix}- {self._apply_dt(item_data)}"
                    output_lines.append(f"i{display_text}\t\t{host}\t{port}")
                
                # Handle dictionary list items (can contain paragraphs and/or nested lists).
                elif isinstance(item_data, dict):
                    if "p" in item_data:
                        display_text = f"{indent_prefix}- {self._apply_dt(item_data['p'])}"
                        output_lines.append(f"i{display_text}\t\t{host}\t{port}")
                    
                    # Recursively render nested unordered lists.
                    if "ul" in item_data:
                        output_lines.extend(_render_list(item_data["ul"], indent=indent + 2, is_ordered=False))
                    # Recursively render nested ordered lists.
                    if "ol" in item_data:
                        output_lines.extend(_render_list(item_data["ol"], indent=indent + 2, is_ordered=True))
                else:
                    # Fallback for unexpected item types, treating them as strings.
                    display_text = f"{indent_prefix}- {self._apply_dt(str(item_data))}"
                    output_lines.append(f"i{display_text}\t\t{host}\t{port}")
            return output_lines


        # Iterate through each parsed Markdown block to convert it to Gophermap.
        for block in blocks:
            # Render Paragraphs
            if "p" in block:
                # Get paragraph content, apply placeholders, and replace tabs for Gophermap compatibility.
                paragraph_display = self._apply_dt(str(block["p"])).replace("\t", " ")
                gopher_lines.append(f"i{paragraph_display}\t\t{host}\t{port}")
            
            # Render H1 Headings (other headings are typically just text in Gophermap)
            elif "h1" in block:
                heading_display = "# " + self._apply_dt(str(block["h1"]))
                gopher_lines.append(f"i{heading_display}\t\t{host}\t{port}")
            
            # Render Unordered Lists
            elif "ul" in block:
                gopher_lines.extend(_render_list(block["ul"], indent=0, is_ordered=False))
            
            # Render Ordered Lists
            elif "ol" in block:
                gopher_lines.extend(_render_list(block["ol"], indent=0, is_ordered=True))
            
            # Render Code Blocks
            elif "code" in block:
                code_content = block["code"].get("text", "")
                # Each line of the code block is an informational Gophermap line.
                for code_line in code_content.splitlines():
                    gopher_lines.append(f"i{self._apply_dt(code_line)}\t\t{host}\t{port}")

        # Gopher protocol historically expects CRLF (Carriage Return Line Feed) as line endings.
        return "\r\n".join(gopher_lines) + "\r\n"


# Backwards-compatible thin wrappers


def render_block(block: dict[str, Any]) -> str:


    """Renders a single Markdown block dictionary into its HTML string representation.





    This is a convenience wrapper that instantiates `HTMLRenderer` and calls its `render_block` method.


    It's provided for backward compatibility.





    Args:


        block: A dictionary representing a single parsed Markdown block.





    Returns:


        An HTML string for the given block.


    """





    return HTMLRenderer().render_block(block)








def render_blocks(blocks: list[dict[str, Any]], fmt: str = "html", title: str | None = None, description: str | None = None, date: str | None = None, time: str | None = None) -> str:


    """Renders a list of Markdown block dictionaries into a specified output format.





    This is a convenience wrapper function that dispatches the rendering task


    to the appropriate renderer class (HTMLRenderer, GemtextRenderer, or GopherRenderer)


    based on the `fmt` argument. It's provided for backward compatibility.





    Args:


        blocks: A list of dictionaries, each representing a parsed Markdown block.


        fmt: The desired output format ("html", "gemini", or "gopher"). Defaults to "html".


        title: The title of the document.


        description: A brief description of the document.


        date: The current date string for placeholder replacement.


        time: The current time string for placeholder replacement.





    Returns:


        A string representing the fully rendered document content in the specified format.


    """





    fmt_lower = (fmt or "").lower() # Ensure format is lowercase for comparison.


    


    if fmt_lower == "html":


        # Render HTML using HTMLRenderer, passing all relevant metadata.


        return HTMLRenderer().render_blocks(blocks, title=title, description=description, date=date, time=time)


    


    if fmt_lower == "gemini" or fmt_lower == "gemtext":


        # Render Gemtext using GemtextRenderer, passing relevant metadata.


        return GemtextRenderer().render_blocks(blocks, title=title, description=description, date=date, time=time)


    


    if fmt_lower == "gopher":


        # Render Gophermap using GopherRenderer, passing relevant metadata.


        return GopherRenderer().render_blocks(blocks, title=title, description=description, date=date, time=time)


    


    # Fallback if an unsupported format is requested.


    return "\n\n".join(str(b) for b in blocks)

