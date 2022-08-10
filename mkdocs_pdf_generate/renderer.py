import logging
import os
import sys
from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
from typing import Dict, Optional

from bs4 import BeautifulSoup
from weasyprint import HTML, CSS

from . import cover
from . import toc
from .preprocessor import get_separate as prep_separate
from .styles import style_for_print
from .themes import generic as generic_theme
from .options import Options


class Renderer(object):
    def __init__(self, options: Options):
        self._options = options

        self.theme = self._load_theme_handler()
        self.page_order = []
        self.pgnum = 0
        self.pages = []

    def write_pdf(
        self,
        content: str,
        base_url: str,
        filename: str,
        pdf_metadata: Optional[Dict] = None,
    ):
        self.render_doc(content, base_url, pdf_metadata=pdf_metadata).write_pdf(
            filename
        )

    def render_doc(self, content: str, base_url: str, pdf_metadata: Dict = None):
        soup = BeautifulSoup(content, "html5lib")

        self.inject_pgnum(soup)

        css = style_for_print(self._options, pdf_metadata)
        css.append(CSS(string=self.theme.get_stylesheet()))

        soup = prep_separate(soup, base_url)
        toc.make_toc(soup, self._options)
        cover.make_cover(soup, self._options, pdf_metadata=pdf_metadata)

        html = HTML(string=str(soup))
        return html.render(stylesheets=css)

    # def add_doc(self, content: str, base_url: str, rel_url: str):
    #     pos = self.page_order.index(rel_url)
    #     self.pages[pos] = (content, base_url, rel_url)
    #
    # def write_combined_pdf(self, output_path: str):
    #     rendered_pages = []
    #     for p in self.pages:
    #         if p is None:
    #             self.logger.error('Unexpected error - not all pages were rendered properly')
    #             continue
    #
    #         render = self.render_doc(p[0], p[1], p[2])
    #         self.pgnum += len(render.pages)
    #         rendered_pages.append(render)
    #
    #     flatten = lambda l: [item for sublist in l for item in sublist]
    #     all_pages = flatten([p.pages for p in rendered_pages if p is not None])
    #
    #     rendered_pages[0].copy(all_pages).write_pdf(output_path)

    def add_link(self, content: str, filename: str, _download_name: str = None):
        if _download_name is not None and len(_download_name) > 0:
            _download_name += ".pdf"
        return self.theme.modify_html(content, filename, _download_name)

    def inject_pgnum(self, soup):
        pgnum_counter = soup.new_tag("style")
        pgnum_counter.string = """
        @page :first {{
            counter-reset: __pgnum__ {};    #noqa W291
        }}
        @page {{
            counter-increment: __pgnum__;
        }}
        """.format(
            self.pgnum
        )

        soup.head.append(pgnum_counter)

    @property
    def logger(self) -> logging:
        return self._options.logger

    def _load_theme_handler(self):
        theme = self._options.theme_name
        custom_handler_path = self._options.theme_handler_path
        module_name = "." + (theme or "generic").replace("-", "_")

        if custom_handler_path:
            try:
                spec = spec_from_file_location(
                    module_name, os.path.join(os.getcwd(), custom_handler_path)
                )
                mod = module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod
            except FileNotFoundError as e:
                self.logger.error(
                    'Could not load theme handler {} from custom directory "{}": {}'.format(
                        theme, custom_handler_path, e
                    ),
                    file=sys.stderr,
                )
                pass

        try:
            return import_module(module_name, "mkdocs_pdf_generate.themes")
        except ImportError as e:
            self.logger.error(
                "Could not load theme handler {}: {}".format(theme, e), file=sys.stderr
            )
            return generic_theme
