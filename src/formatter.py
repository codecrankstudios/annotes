import re
from typing import List, Tuple, Dict, Any

def render_page_annotations(
    page_num: int,
    annots: List[Dict[str, Any]],
    annotated_doc,
    config: Dict[str, Any],
    pdf_basename: str = None,
    ranNum=1,
):
    """Render parsed annotations for a single page into the MarkdownBuilder.

    annots: List of annotation dicts (from pdfUtils._parse_annotations output)
            Keys: 'type', 'highlight_text', 'comment', 'rect', 'shape_type'
    annotated_doc: MarkdownBuilder object
    config: full configuration dictionary
    pdf_basename: optional PDF file basename used to build page links
    """
    
    output: List[Tuple[str, int, str]] = []
    # Tuple: (kind: 'heading'|'bullet'|'quote'|'task'|'image', level, text)

    for annot in annots:
        # Filter for the current page if not already filtered
        if annot.get("page") != page_num:
            continue

        comment = (annot.get("comment") or "").strip()
        highlight = (annot.get("highlight_text") or "").strip()
        atype = annot.get("type", "Highlight")

        # --- 1. Image Handling ---
        if atype == "Image":
            # For shapes, we use the comment as the title/filename part
            pix_title = comment.replace("\r", " ").replace("\n", " ")
            if not pix_title:
                pix_title = str(ranNum)
                ranNum += 1
            else:
                # Sanitize filename
                pix_title = "".join(x for x in pix_title if x.isalnum() or x in (' ', '-', '_')).strip()

            nameImg = f"SS_{pdf_basename.replace(' ', '')}(pg{page_num})_{pix_title.replace(' ', '')}.png"
            image_path = f"assets/{pdf_basename}/{nameImg}"
            output.append(("image", 0, image_path))
            continue

        # --- 2. Syntax Parsing for Highlights ---
        a_set = config.get("annotation_settings", {})
        
        def get_triggers(key, default):
            val = a_set.get(key, default)
            if isinstance(val, str):
                return [t.strip() for t in val.split(",") if t.strip()]
            return val if isinstance(val, list) else [default]

        h_triggers = get_triggers("symbol_heading", ".h1")
        q_triggers = get_triggers("symbol_quote", ">>")
        t_triggers = get_triggers("symbol_todo", ".todo")

        # Rule: Headers
        found_h = next((t for t in h_triggers if comment.startswith(t)), None)
        if found_h:
            clean_comment = comment[len(found_h):].strip()
            text = clean_comment if clean_comment else highlight
            output.append(("heading", 1, text))
            continue
        
        # Rule: Quotes
        found_q = next((t for t in q_triggers if comment.startswith(t)), None)
        if found_q or comment.startswith(".q"): # keep .q as hardcoded fallback or override?
            prefix = found_q if found_q else ".q"
            clean_comment = comment[len(prefix):].strip()
            text = highlight
            if clean_comment:
                text += f" **({clean_comment})**"
            output.append(("quote", 1, text))
            continue

        # Rule: Tasks
        found_t = next((t for t in t_triggers if comment.startswith(t)), None)
        if found_t:
            clean_comment = comment[len(found_t):].strip()
            text = highlight
            if clean_comment:
                text += f" - {clean_comment}"
            output.append(("task", 1, text))
            continue

        # Default: Bullet point
        content = highlight
        if comment:
            # Format: Highlight - **Comment**
            content = f"{highlight} \n  - **Note:** {comment}"
        
        if content:
            output.append(("bullet", 0, content))

    # --- 3. Render to MarkdownBuilder ---
    for kind, level, text in output:
        if kind == "heading":
            annotated_doc.add_spacer(1)
            annotated_doc.add_heading(text, level=level)
            
            # Page Link
            try:
                pl_conf = config.get("output_settings", {}).get("page_link_settings", {})
                if pl_conf.get("include_page_links", True):
                    link_text = f"[[{pdf_basename}#page={page_num}]]"
                    visible_flag = pl_conf.get("visible_links", None)
                    is_visible = bool(visible_flag) if visible_flag is not None else (pl_conf.get("link_style", "hidden") == "visible")
                    
                    if not is_visible:
                         link_text = f"%%{link_text}%%"
                    annotated_doc.content += f"{link_text}\n"
            except Exception:
                pass
            annotated_doc.add_spacer(1)
            
        elif kind == "image":
            annotated_doc.add_bullet_point(f"![[{text}]]", level=1)
            
        elif kind == "quote":
            annotated_doc.add_blockquote(text)
            
        elif kind == "task":
            # Manual formatted task
            annotated_doc.content += f"- [ ] {text}\n"
            
        else: # bullet
            annotated_doc.add_bullet_point(text, level=1)

    return ranNum
