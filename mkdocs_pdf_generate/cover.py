import re
from typing import Dict

from bs4 import BeautifulSoup, Tag

from .options import Options
from .templates.filters.url import URLFilter


def make_cover(soup: BeautifulSoup, options: Options, pdf_metadata: Dict):
    """
    Generate a cover page if the 'cover' option is enabled.

    :param soup: The target element.
    :param options: Project options.
    :param pdf_metadata: Metadata for the PDF.
    """

    if options.cover:
        _make_cover(soup, options, pdf_metadata)


def _make_cover(soup: BeautifulSoup, options: Options, pdf_metadata: Dict):
    """
    Generate a cover page for a PDF document and add it to the provided BeautifulSoup object.

    .. note::

        This function modifies the input BeautifulSoup object in-place by inserting a cover page.

    :param soup: The BeautifulSoup object representing the document's HTML.
    :param options: An instance of the Options class containing various configuration settings.
    :param pdf_metadata: Metadata for the PDF document.

    :return: The modified BeautifulSoup object with the cover page inserted.
    :raise Exception: If there's an error during cover page generation.


    """
    try:
        keywords = options.template.keywords
        keywords["site_url"] = re.sub(r"http://|https://", "", keywords["site_url"])
        # Set cover title
        keywords["cover_title"] = pdf_metadata.get("title") or options.body_title or keywords["cover_title"]
        # Set cover image
        document_type: str = pdf_metadata.get("type", "Documentation")
        path_filter = URLFilter(options, options.user_config)
        if options.cover_images is not None:
            cover_images = {
                str(img_k).lower(): path_filter(pathname=str(img_v)) for img_k, img_v in options.cover_images.items()
            }
            keywords["cover_image"] = cover_images.get(document_type.lower()) or cover_images.get("default")
        # Set cover sub_title
        keywords["cover_subtitle"] = (
            pdf_metadata.get("subtitle") or document_type.capitalize() or keywords["cover_subtitle"]
        )
        keywords["revision"] = pdf_metadata.get("revision") or None
        # Populate local options into template keywords
        keywords.update(pdf_metadata)

        # Select cover template
        cover_template_files = [document_type.lower(), "cover", "default_cover"]
        template = options.template.select(cover_template_files)
        options.logger.info(f'Generate cover page for PDF document using "{template.name}" template.')

        def str_to_bs4(html_like_str: str) -> Tag:
            """Convert an HTML-like string to a BeautifulSoup Tag."""
            html_soup = BeautifulSoup(html_like_str, "html.parser")
            return html_soup

        cover_template = str(template.render(keywords))
        cover_html = str_to_bs4(cover_template)

        # Remove h1 content
        h1_title = soup.find("h1", attrs={"id": re.compile(r"[\w_\-]+")})
        if h1_title is not None:
            h1_title.decompose()

        # Insert cover_html at the beginning of the document
        soup.body.insert(0, cover_html)
    except Exception as e:
        options.logger.error(f"Failed to add cover page: {str(e)}")
        return soup
