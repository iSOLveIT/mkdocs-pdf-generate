import html
import os
from typing import Dict

import sass

from ..options import Options

from weasyprint import CSS


def _css_escape(text: str) -> str:
    """@see https://developer.mozilla.org/en-US/docs/Web/CSS/string"""

    if not text:
        return ""

    text = html.unescape(str(text))

    # -- probably not needed.
    # text = text.encode('unicode-escape').decode('ascii').replace('\\u', '\\')

    return text.replace("'", "\\27")


def style_for_print(options: Options, pdf_metadata: Dict = None) -> list[CSS]:
    scss = f"""
    :root {{
        --author: '{_css_escape(options.author)}',
        --author_logo: url('{_css_escape(options.author_logo)}'),
        --copyright: '{_css_escape(options.copyright)}',
        --title: '{_css_escape(pdf_metadata.get("title", options.cover_title))}',
        --subtitle: '{_css_escape(pdf_metadata.get("subtitle", options.cover_subtitle))}',
        --type: '{_css_escape(pdf_metadata.get("type", "Documentation"))}',
        --revision: '{_css_escape(pdf_metadata.get("revision", ""))}',
        --filename: '{_css_escape(pdf_metadata.get("filename", ""))}';
    }}
    h1 {{
        string-set: chapter content();
    }}
    """
    css = sass.compile(string=scss)

    css_files = [CSS(string=css)]

    base_path = os.path.abspath(os.path.dirname(__file__))

    filename = os.path.join(base_path, "pdf-print.css")
    css_files.append(CSS(filename=filename))

    if options.cover:
        filename = os.path.join(base_path, "cover.css")
        css_files.append(CSS(filename=filename))

    # docs_src_dir = os.path.abspath(os.path.dirname(self._config["config_file_path"]))
    # custom_template_path = self._options.custom_template_path
    # filename = os.path.join(options.custom_template_path, "custom.css")
    # if os.path.exists(filename):
    #     css_files.append(CSS(filename=filename))

    return css_files
