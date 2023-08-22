import os
import re
from typing import Dict, Optional, Union

from bs4 import BeautifulSoup, Tag

from .options import Options


def get_pdf_metadata(metadata: Dict) -> Dict:
    """
    Extracts PDF metadata from a given metadata dictionary.

    :param metadata: The metadata dictionary containing PDF-related information.
    :return: A dictionary containing PDF metadata. If no PDF metadata is found,
              an empty dictionary is returned.
    """
    pdf_meta = metadata.get("pdf", {}) if "pdf" in metadata and metadata["pdf"] is not None else {}
    return pdf_meta


def secure_filename(filename: str) -> str:
    r"""Pass it a filename, and it will return a secure version of it. This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`. The filename returned is an ASCII only string
    for maximum portability.

    On Windows systems the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename(u'i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you generate random
    filename if the function returned an empty one.

    :param filename: the filename to secure
    """
    _filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
    _windows_device_files = (
        "CON",
        "AUX",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "LPT1",
        "LPT2",
        "LPT3",
        "PRN",
        "NUL",
    )

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip("._")

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if os.name == "nt" and filename and filename.split(".")[0].upper() in _windows_device_files:
        filename = "_" + filename

    return filename


def extract_h1_title(content: Union[str, Tag], page_metadata: Dict) -> Optional[str]:
    """
    Extracts and returns the H1 title from the given HTML content or returns the
     page metadata title if no H1 title is found.

    :param content: HTML content as a string or BeautifulSoup PageElement.
    :param page_metadata: Metadata dictionary containing page information.

    :return: Extracted H1 title or page metadata title if H1 title is not found.
    """
    soup = content
    if isinstance(soup, str):
        soup = BeautifulSoup(soup, "html.parser")

    title_element = soup.find("h1", attrs={"id": re.compile(r"[\w_\-]+")})
    if title_element is None:
        return page_metadata.get("title")

    title_text = title_element.text
    title_text = re.sub(r"^[\d.]+ ", "", title_text)
    return title_text


def enable_legal_terms(soup: BeautifulSoup, options: Options, pdf_metadata: Dict) -> Tag:
    """
    Enable and add legal_terms section to the PDF document content.

    .. note::

        This function modifies the input BeautifulSoup object in-place by inserting a legal_terms page.

    :param soup: The BeautifulSoup object representing the document's content.
    :param options: The options for the PDF generation process.
    :param pdf_metadata: The metadata associated with the PDF.

    :return: The modified BeautifulSoup object with added legal_terms content.
    :raise Exception: If there's an error during legal_terms page generation.
    """
    try:
        content = soup.find("article", attrs={"class": "md-content__inner"})
        # Set legal_terms to document's legal_terms local option
        document_legal_terms: str = pdf_metadata.get("legal_terms", "legal_terms")
        # Select legal_terms template
        legal_terms_template_files = [document_legal_terms.lower()]
        template = options.template.select(legal_terms_template_files)

        options.logger.info(f'Add legal_terms content to PDF document using "{template.name}" template.')
        legal_terms_template = str(template.render())

        def format_legal_terms_html(legal_terms_html: str) -> Tag:
            """
            Format legal_terms HTML to a BeautifulSoup Tag.

            :param legal_terms_html: The HTML content of the legal_terms.
            :return: The BeautifulSoup Tag with the added legal_terms content.
            """
            html_soup = BeautifulSoup(legal_terms_html, "html.parser")
            headings = html_soup.find_all(["h2", "h3", "h4", "h5", "h6"])
            for h in headings:
                ref = h.get("id")
                if ref is None:
                    h["id"] = generate_heading_id(h.string)
            return html_soup

        # Create legal_terms div wrapper
        legal_terms_div = soup.new_tag(
            "div",
            attrs={
                "id": "mkdocs-pdf-gen-legal-terms",
                "class": "page-break",
            },
        )
        legal_terms_div.append(format_legal_terms_html(legal_terms_template))

        content.append(legal_terms_div)
        return soup
    except Exception as e:
        options.logger.error(f"Failed to add legal_terms: {str(e)}")
        return soup


def generate_heading_id(input_string: str) -> str:
    """
    Generate MkDocs appropriate ids for heading tags.

    :param input_string: The input string that needs to be processed.
    :return: The modified string with spaces replaced by hyphens and symbols removed.
    """
    # Replace spaces with hyphens
    modified_string = re.sub(r"\s+", "-", input_string)

    # Remove symbols using regex pattern [^\w\s-]
    modified_string = re.sub(r"[^\w\s-]", "", modified_string)

    return modified_string.replace("--", "-").lower()
