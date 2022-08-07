import re
from typing import Dict

from bs4 import PageElement, BeautifulSoup

from .options import Options
from .templates.filters.url import URLFilter
from .utils import secure_filename, h1_title


def make_cover(soup: PageElement, options: Options, pdf_metadata: Dict = None):
    """Generate a cover pages.

    Arguments:
        soup {BeautifulSoup} -- target element.
        options {Options} -- the project options.
    """

    if options.cover:
        _make_cover(soup, options, pdf_metadata)


def _make_cover(soup: PageElement, options: Options, pdf_metadata: Dict = None):

    try:
        keywords = options.template.keywords
        # Set cover title
        keywords["cover_title"] = (
            pdf_metadata.get("title") or h1_title(soup) or keywords["cover_title"]
        )
        # Set cover image
        document_type: str = pdf_metadata.get("type", "Documentation")
        path_filter = URLFilter(options)
        cover_images = {
            str(img_k).lower(): path_filter(pathname=str(img_v))
            for img_k, img_v in options.cover_images.items()
        }
        keywords["cover_image"] = cover_images.get(
            document_type.lower()
        ) or cover_images.get("default")
        # Set cover sub_title
        keywords["cover_subtitle"] = (
            pdf_metadata.get("subtitle")
            or document_type.capitalize()
            or keywords["cover_subtitle"]
        )
        # Populate local options into template keywords
        keywords.update(pdf_metadata)

        # Select cover template
        template = options.template.select(["cover", "default_cover"])

        options.logger.info(f'Generate a cover page with "{template.name}".')
        soup_template = BeautifulSoup(template.render(keywords), "html5lib")

        soup.body.insert(0, soup_template)
    except Exception as e:
        options.logger.error("Failed to generate the cover page: %s", e)
