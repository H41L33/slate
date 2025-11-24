"""Parse Markdown text into block dicts for rendering."""

from typing import Any

from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin

CALLOUTS = ("NOTE", "WARNING", "DANGER", "SUCCESS", "TIP")


def parse_markdown_to_dicts(mdtext: str) -> list[dict[str, Any]]:
    md = (
        MarkdownIt('commonmark', {'breaks':True,'html':True})
        .use(front_matter_plugin)
        .enable('table')
    )
    md.use(front_matter_plugin)
    md.enable("table")
    tokens = md.parse(mdtext)
    result: list[dict[str, Any]] = []
    i = 0
    
    def parse_list_at(tokens: Any, idx: int) -> tuple[dict[str, Any], int]:
        """Parse a bullet or ordered list starting at tokens[idx].

        Returns (list_block_dict, new_index) where list_block_dict is
        {'ul': [...]} or {'ol': [...]} and new_index is the token index
        after the corresponding list_close.
        """
        start = tokens[idx]
        is_ordered = start.type == "ordered_list_open"
        list_key = "ol" if is_ordered else "ul"
        items: list[Any] = []
        j = idx + 1
        # iterate until list_close
        close_type = "ordered_list_close" if is_ordered else "bullet_list_close"
        while j < len(tokens) and tokens[j].type != close_type:
            tok = tokens[j]
            if tok.type == "list_item_open":
                # parse contents of list item
                k = j + 1
                item_text = None
                nested_list = None
                # accumulate paragraph lines into item_text if present
                while k < len(tokens) and tokens[k].type != "list_item_close":
                    t = tokens[k]
                    if t.type == "paragraph_open":
                        if k + 1 < len(tokens) and tokens[k+1].type == "inline":
                            item_text = tokens[k+1].content
                            k += 2
                            continue
                        k += 1
                    elif t.type in ("bullet_list_open", "ordered_list_open"):
                        nested, newk = parse_list_at(tokens, k)
                        nested_list = nested
                        k = newk
                        continue
                    else:
                        k += 1
                # build item representation: either string, or dict with 'p' and nested list
                if nested_list and item_text:
                    item: Any = {"p": item_text}
                    item.update(nested_list)
                elif nested_list:
                    # item that contains only a nested list: represent as nested list directly
                    # but wrap into a dict so renderer can detect nested structure
                    item = nested_list
                else:
                    item = item_text or ""

                items.append(item)
                j = k + 1
            else:
                j += 1

        return ({list_key: items}, j + 1)

    while i < len(tokens):
        token = tokens[i]

        # Headings
        if token.type == "heading_open":
            tag = f"h{token.tag[1]}"
            text = tokens[i+1].content if tokens[i+1].type == "inline" else ""
            result.append({tag: text})
            i += 2  # skip inline & close
            continue

        # Paragraphs and callouts
        if token.type == "paragraph_open":
            content = tokens[i+1].content if tokens[i+1].type == "inline" else ""
            callout_match = None
            for callout in CALLOUTS:
                # Match [!NOTE] (with optional exclamation mark—some use [NOTE])
                if content.strip().upper().startswith(f"[!{callout}]"):
                    callout_match = callout
                    stripped = content.strip()[len(f"[!{callout}]"):].strip()
                    result.append({f"callout-{callout.lower()}": stripped})
                    break
            if not callout_match:
                result.append({"p": content})
            i += 2
            continue

        # Blockquotes
        if token.type == "blockquote_open":
            bq_content = ""
            j = i + 1
            while tokens[j].type != "blockquote_close":
                if tokens[j].type == "inline":
                    bq_content += tokens[j].content
                j += 1
            result.append({"blockquote": bq_content})
            i = j + 1
            continue

        # Image in inline
        if token.type == "inline":
            for child in getattr(token, "children", []):
                if child.type == "image":
                    result.append({"image": {
                        "src": child.attrs.get("src", ""),
                        "alt": child.attrs.get("alt", ""),
                        "caption": child.attrs.get("title", "")
                    }})
            i += 1
            continue

        # Code block (fenced)
        if token.type == "fence":
            result.append({"code": {
                "text": token.content,
                "lang": token.info or ""
            }})
            i += 1
            continue

        # Unordered list
        if token.type == "bullet_list_open":
            lst, newi = parse_list_at(tokens, i)
            result.append(lst)
            i = newi
            continue

        # Ordered list
        if token.type == "ordered_list_open":
            lst, newi = parse_list_at(tokens, i)
            result.append(lst)
            i = newi
            continue

        # Table parsing
        if token.type == "table_open":
            headers: list[str] = []
            rows: list[list[str]] = []
            # Find headers
            j = i + 1
            while tokens[j].type != "thead_close":
                if tokens[j].type == "th_open":
                    headers.append(tokens[j+1].content)
                j += 1
            # Find rows in tbody
            k = j + 1
            while tokens[k].type != "table_close":
                if tokens[k].type == "td_open":
                    row = []
                    k += 1
                    while tokens[k].type != "tr_close":
                        if tokens[k].type == "inline":
                            row.append(tokens[k].content)
                        k += 1
                    rows.append(row)
                else:
                    k += 1
            result.append({"table": {"headers": headers, "rows": rows}})
            i = k + 1
            continue

        i += 1

    return result