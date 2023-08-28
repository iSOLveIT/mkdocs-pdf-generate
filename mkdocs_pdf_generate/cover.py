import re
from typing import Dict, Optional

from bs4 import BeautifulSoup, Tag
from pathlib import Path

from .options import Options
from .templates.filters.url import URLFilter


class PDFPluginException(Exception):
    """
    Custom exception class for PDF plugin errors.
    """

    pass


def make_cover(soup: BeautifulSoup, options: Options, pdf_metadata: Dict) -> None:
    """
    Generate a cover page if the 'cover' option is enabled.

    :param soup: The target element.
    :param options: Project options.
    :param pdf_metadata: Metadata for the PDF.
    """

    if options.cover:
        _make_cover(soup, options, pdf_metadata)


def _make_cover(soup: BeautifulSoup, options: Options, pdf_metadata: Dict) -> Optional[BeautifulSoup]:
    """
    Generate a cover page for a PDF document and add it to the provided BeautifulSoup object.

    .. note::

        This function modifies the input BeautifulSoup object in-place by inserting a cover page.

    :param soup: The BeautifulSoup object representing the document's HTML.
    :param options: An instance of the Options class containing various configuration settings.
    :param pdf_metadata: Metadata for the PDF document.

    :return: The modified BeautifulSoup object with the cover page inserted or None.
    """
    try:
        keywords = options.template.keywords
        keywords["site_url"] = re.sub(r"http://|https://", "", keywords["site_url"])
        # Set cover title
        keywords["cover_title"] = pdf_metadata.get("title") or options.body_title or keywords["cover_title"]
        # Set cover image
        document_type: str = pdf_metadata.get("type") or "Documentation"
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
        keywords["revision"] = pdf_metadata.get("revision")
        # Populate local options into template keywords
        keywords.update({k: v for k, v in pdf_metadata.items() if k != "cover_image"})

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

        # Include an image on the cover page
        def include_image(cover_page_html: Tag) -> Tag:
            """Convert an HTML-like string to a BeautifulSoup Tag."""
            # Get cover-image local option
            cover_page_image = pdf_metadata.get("cover_image")
            if not cover_page_image:
                return cover_page_html
            try:
                cover_img_id, cover_img_source, cover_img_css = cover_page_image.values()
            except ValueError:
                raise PDFPluginException(
                    "Missing required options for the 'cover_image' local option in the PDF markdown metadata."
                )
            # Parse relative cover image source to absolute path
            doc_src_path = path_filter(pathname=str(options.md_src_path)).replace("file://", "")
            abs_cover_img_source = Path(doc_src_path).parent.joinpath(cover_img_source).resolve()

            # Get cover image HTML tag
            cover_img_tag = cover_page_html.find(attrs={"id": cover_img_id})
            if not cover_img_tag:
                options.logger.error(
                    f"No HTML element in your cover template ('{template.name}') "
                    f"has an 'id' attribute equal to `{cover_img_id}`."
                )
                return cover_page_html

            # Add user-specified information to cover image tag
            default_css = (
                f"position: absolute; background-image: url('{abs_cover_img_source.as_uri()}'); "
                f"background-size: contain; background-repeat: no-repeat;"
            )
            cover_img_tag["style"] = f"{default_css}{cover_img_css}"
            # Inform user when the image file provided doesn't exist
            if not abs_cover_img_source.exists():
                cover_img_tag.string = f"Image file not found - <{cover_img_source}>"
                options.logger.error(
                    f"The cover image source you provided for {options.md_src_path} does not exist. "
                    f"Path: '{cover_img_source}'"
                )
            return cover_page_html

        # Add cover image to cover HTML
        cover_html = include_image(cover_html)

        # Remove h1 content
        h1_title = soup.find("h1", attrs={"id": re.compile(r"[\w_\-]+")})
        if h1_title is not None:
            h1_title.decompose()

        # Insert cover_html at the beginning of the document
        soup.body.insert(0, cover_html)
    except Exception as e:
        options.logger.error(f"Failed to add cover page: {str(e)}")
        return soup
