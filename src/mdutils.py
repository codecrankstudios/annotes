import settings


class MarkdownBuilder:
    """
    A builder class to programmatically construct a Markdown document string.

    Attributes:
        content (str): The accumulated Markdown content string.
    """

    def __init__(self):
        """Initializes the MarkdownBuilder with empty content."""
        self.content = ""

    def add_yaml_front_matter(self, front_matter_dict):
        """
        Adds a YAML front matter block to the start of the document.

        Args:
            front_matter_dict (dict): A dictionary of key-value pairs for the front matter.
        """
        self.content += "---\n"
        for key, value in front_matter_dict.items():
            self.content += f"{key}: {value}\n"
        self.content += "---\n\n"

    def add_heading(self, text, level=1):
        """
        Adds a heading.

        Args:
            text (str): The heading text.
            level (int, optional): The heading level (1-6). Defaults to 1.
        """
        self.content += f"{'#' * level} {text}\n\n"

    def add_bullet_point(self, text, level=1):
        """
        Adds an indented bullet point.

        Args:
            text (str): The list item text.
            level (int, optional): The indentation level. Defaults to 1.
        """
        tab_size = settings.CONFIG["markdown_settings"].get("tab_size", 4)
        indent = " " * tab_size * (level - 1)
        self.content += f"{indent}- {text}\n"

    def add_numbered_point(self, text, number, level=1):
        """
        Adds an indented numbered list item.

        Args:
            text (str): The list item text.
            number (int): The number for the list item.
            level (int, optional): The indentation level. Defaults to 1.
        """
        tab_size = settings.CONFIG["markdown_settings"].get("tab_size", 4)
        indent = " " * tab_size * (level - 1)
        self.content += f"{indent}{number}. {text}\n"

    def add_horizontal_rule(self):
        """Adds a horizontal rule."""
        self.content += "\n---\n\n"

    def add_blockquote(self, text, level=1):
        """
        Adds an indented blockquote.

        Args:
            text (str): The quote text.
            level (int, optional): The indentation level. Defaults to 1.
        """
        tab_size = settings.CONFIG["markdown_settings"].get("tab_size", 4)
        indent = " " * tab_size * (level - 1)
        self.content += f"{indent}> {text}\n\n"

    def add_code_block(self, code, language="", level=1):
        """
        Adds a fenced code block.

        Args:
            code (str): The code to include in the block.
            language (str, optional): The language for syntax highlighting. Defaults to "".
            level (int, optional): The indentation level. Defaults to 1.
        """
        tab_size = settings.CONFIG["markdown_settings"].get("tab_size", 4)
        indent = " " * tab_size * (level - 1)
        self.content += f"{indent}```{language}\n{code}\n```\n\n"

    def add_inline_code(self, text):
        """
        Adds inline code formatting.

        Args:
            text (str): The text to format as inline code.
        """
        self.content += f"`{text}`"

    def add_image(self, image_path, alt_text="", level=1):
        """
        Adds an image link, supporting standard and wikilink styles.

        Args:
            image_path (str): The path to the image.
            alt_text (str, optional): The alt text for the image. Defaults to "".
            level (int, optional): The indentation level. Defaults to 1.
        """
        tab_size = settings.CONFIG["markdown_settings"].get("tab_size", 4)
        indent = " " * tab_size * (level - 1)

        if (
            settings.CONFIG["markdown_settings"].get("image_style", "wikilinks")
            == "wikilinks"
        ):
            self.content += f"{indent}![[{alt_text}|{image_path}]]\n\n"
        else:
            self.content += f"{indent}![{alt_text}]({image_path})\n\n"

    def add_link(self, text, url):
        """
        Adds a hyperlink, supporting standard and wikilink styles.

        Args:
            text (str): The link's display text.
            url (str): The link's destination URL.
        """
        if (
            settings.CONFIG["markdown_settings"].get("linking_style", "wikilinks")
            == "wikilinks"
        ):
            self.content += f"[[{text}|{url}]]"
        else:
            self.content += f"[{text}]({url})"

    def add_bold(self, text):
        """Wraps text in bold formatting."""
        self.content += f"**{text}**"

    def add_italic(self, text):
        """Wraps text in italic formatting."""
        self.content += f"*{text}*"

    def add_strikethrough(self, text):
        """Wraps text in strikethrough formatting."""
        self.content += f"~~{text}~~"

    def save(self, file_path):
        """
        Saves the accumulated Markdown content to a file.

        Args:
            file_path (str or Path): The path to the output Markdown file.
        """
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.content)
        return file_path

    def add_admonitions(
        self, title="", text="", admonition_type="note", level=1, collapsed=False
    ):
        """
        Adds an admonition block.

        Args:
            title (str): The title of the admonition. Defaults to "".
            text (str): The admonition text.
            admonition_type (str, optional): The type of admonition (e.g., "note", "warning").
                Defaults to "note".
            level (int, optional): The indentation level. Defaults to 1.
        """
        tab_size = settings.CONFIG["markdown_settings"].get("tab_size", 4)
        indent = " " * tab_size * (level - 1)
        self.content += f"{indent}![{admonition_type}] {title}\n"
        for line in text.splitlines():
            self.content += f"{indent}    {line}\n"
        self.content += "\n"

    def add_spacer(self, lines=1):
        """
        Adds vertical space by inserting blank lines.

        Args:
            lines (int, optional): The number of blank lines to add. Defaults to 1.
        """
        self.content += "\n" * lines


def generate_list_from_items(items, ordered=False):
    """
    Generates a Markdown list from a list of items.

    Args:
        items (list): A list of strings representing the list items.
        ordered (bool, optional): Whether to create an ordered (numbered) list.
            Defaults to False.
        level (int, optional): The indentation level. Defaults to 1.
    """
    tab_size = settings.CONFIG["markdown_settings"].get("tab_size", 4)
    indent = " " * tab_size

    if ordered:
        return "\n".join(f"{indent}{i + 1}. {item}" for i, item in enumerate(items))
    else:
        return "\n".join(f"{indent}- {item}" for item in items)
