import html
import os
from typing import Dict

# import sass

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
    }}
    h1 {{
        string-set: chapter content();
    }}
    """.format(
        _css_escape(options.author),
        _css_escape(options.author_logo),
        _css_escape(options.copyright),
        _css_escape(pdf_metadata.get("title", options.cover_title)),
        _css_escape(pdf_metadata.get("subtitle", options.cover_subtitle)),
        _css_escape(pdf_metadata.get("type", "Documentation")),
        _css_escape(pdf_metadata.get("revision", "")),
        _css_escape(pdf_metadata.get("filename", "")),
        _css_escape(options.site_url),
    )
    css_files = [CSS(string=css_string)]

    base_path = os.path.abspath(os.path.dirname(__file__))

    filename = os.path.join(base_path, "pdf-print.css")
    css_files.append(CSS(filename=filename))

    if options.toc:
        filename = os.path.join(base_path, "toc.css")
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
