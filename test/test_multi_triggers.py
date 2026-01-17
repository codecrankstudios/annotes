import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from formatter import render_page_annotations
import yaml

class MockDoc:
    def __init__(self):
        self.content = ""
    def add_spacer(self, n): self.content += "\n" * n
    def add_heading(self, text, level): self.content += f"{'#' * level} {text}\n"
    def add_bullet_point(self, text, level): self.content += f"{'  ' * level}- {text}\n"
    def add_blockquote(self, text): self.content += f"> {text}\n"

def test_multi_triggers():
    config = {
        "annotation_settings": {
            "symbol_quote": ">>, .quote",
            "symbol_todo": ".todo, - [ ]",
            "symbol_heading": ".h1, #",
            "symbol_indent": "-"
        },
        "output_settings": {
            "page_link_settings": {"include_page_links": False}
        }
    }

    annots = [
        {"page": 1, "type": "Highlight", "highlight_text": "Text 1", "comment": ".todo Task 1"},
        {"page": 1, "type": "Highlight", "highlight_text": "Text 2", "comment": "- [ ] Task 2"},
        {"page": 1, "type": "Highlight", "highlight_text": "Text 3", "comment": ">> Quote 1"},
        {"page": 1, "type": "Highlight", "highlight_text": "Text 4", "comment": ".quote Quote 2"},
        {"page": 1, "type": "Highlight", "highlight_text": "Text 5", "comment": ".h1 Header 1"},
        {"page": 1, "type": "Highlight", "highlight_text": "Text 6", "comment": "# Header 2"},
    ]

    doc = MockDoc()
    render_page_annotations(1, annots, doc, config, pdf_basename="test.pdf")

    print("Generated Content:")
    print(doc.content)

    # Assertions
    assert "- [ ] Text 1 - Task 1" in doc.content
    assert "- [ ] Text 2 - Task 2" in doc.content
    assert "> Text 3 **(Quote 1)**" in doc.content
    assert "> Text 4 **(Quote 2)**" in doc.content
    assert "# Header 1" in doc.content
    assert "# Header 2" in doc.content
    
    print("\n✅ Multi-trigger verification successful!")

if __name__ == "__main__":
    test_multi_triggers()
