import html
import re
from pathlib import Path
from typing import Dict, List

from bs4 import Tag

from ..options import Options


def _css_escape(text: str) -> str:
    """
    Escape a string for safe use in CSS.

    This function escapes a string to be safely used as a value in a CSS property.
    It performs HTML un-escaping on the input text to handle any HTML entities that might be present.

    See Also:
        - `MDN documentation <https://developer.mozilla.org/en-US/docs/Web/CSS/string>`_

    :param text: The input string to be escaped.
    :return: The escaped string safe for use in CSS.
    """

    if not text:
        return ""

    text = html.unescape(str(text))
    return text.replace("'", "\\27")


def style_for_print(options: Options, pdf_metadata: Dict) -> List[Tag]:
    """
    Generate a list of CSS style tags for printing documentation.

    :param options: An Options object containing various styling options.
    :param pdf_metadata: Metadata for the PDF.
    :return: A list of Tag objects representing CSS styles.
    """
    base_path = Path(__file__).parent.resolve()

    css_string = """
    :root {{
        --author: '{}';
        --author-logo: url('{}');
        --copyright: '{}';
        --title: '{}';
        --subtitle: '{}';
        --type: '{}';
        --revision: '{}';
        --filename: '{}';
        --site-url: '{}';
        --base-page-orientation: a4 portrait;
        --rotated-page-orientation: a4 landscape;
    }}""".format(
        _css_escape(options.author),
        _css_escape(options.author_logo),
        _css_escape(options.copyright),
        _css_escape(pdf_metadata.get("title", options.body_title or options.cover_title)),
        _css_escape(pdf_metadata.get("subtitle", options.cover_subtitle)),
        _css_escape(pdf_metadata.get("type", "Documentation")),
        _css_escape(pdf_metadata.get("revision", "")),
        _css_escape(pdf_metadata.get("filename", "")),
        _css_escape(re.sub(r"http://|https://", "", options.site_url)),
    )
    css_tag = Tag(name="style", attrs={"class": "plugin-default-css"})
    css_tag.append(css_string)
    css_files = ["_styles.css", "_paging.css"]

    if options.toc:
        css_files.append("toc.css")

    if options.cover:
        css_files.append("cover.css")

    docs_src_dir = Path(options.user_config["config_file_path"]).parent.resolve()
    custom_template_path = Path(options.custom_template_path)
    if not custom_template_path.is_absolute():
        custom_template_path = docs_src_dir.joinpath(options.custom_template_path)

    if custom_template_path.is_dir():
        css_files.append("custom.css")  # Add plugin custom CSS

    css_styles_list: List[Tag] = []
    for css_file in css_files:
        filename = base_path.joinpath(css_file) if css_file != "custom.css" else custom_template_path.joinpath(css_file)
        if filename.is_file():
            with open(filename, "r", encoding="UTF-8") as f:
                css_rules = f.read()
                if css_file in ["_styles.css", "_paging.css"]:
                    css_tag.append(css_rules)
                else:
                    style_tag = Tag(
                        name="style",
                        attrs={"class": "plugin-{}".format(css_file.replace(".", "-"))},
                    )
                    style_tag.append(css_rules)
                    css_styles_list.append(style_tag)

    css_styles_list.insert(0, css_tag)  # Insert default CSS tag at the start
    return css_styles_list
