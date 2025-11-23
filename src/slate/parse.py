"""Parse Markdown text into block dicts for rendering."""

from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin

CALLOUTS = ("NOTE", "WARNING", "DANGER", "SUCCESS", "TIP")

def parse_markdown_to_dicts(mdtext: str):
    md = (
        MarkdownIt('commonmark', {'breaks':True,'html':True})
        .use(front_matter_plugin)
        .enable('table')
    )
    md.use(front_matter_plugin)
    md.enable("table")
    tokens = md.parse(mdtext)
    result = []
    i = 0
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
        elif token.type == "paragraph_open":
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
        elif token.type == "blockquote_open":
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
        elif token.type == "inline":
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
        elif token.type == "fence":
            result.append({"code": {
                "text": token.content,
                "lang": token.info or ""
            }})
            i += 1
            continue

        # Unordered list
        elif token.type == "bullet_list_open":
            items = []
            j = i + 1
            while tokens[j].type != "bullet_list_close":
                if tokens[j].type == "inline":
                    items.append(tokens[j].content)
                j += 1
            result.append({"ul": items})
            i = j + 1
            continue

        # Ordered list
        elif token.type == "ordered_list_open":
            items = []
            j = i + 1
            while tokens[j].type != "ordered_list_close":
                if tokens[j].type == "inline":
                    items.append(tokens[j].content)
                j += 1
            result.append({"ol": items})
            i = j + 1
            continue

        # Table parsing
        elif token.type == "table_open":
            headers = []
            rows = []
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

        else:
            i += 1

    return result