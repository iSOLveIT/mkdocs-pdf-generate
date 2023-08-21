from typing import Optional

from bs4 import BeautifulSoup


def get_stylesheet() -> Optional[str]:
    """
    Get the stylesheet for the HTML.

    :return: The stylesheet content, or None if no stylesheet is available.
    """
    return None


def modify_html(html: str, href: str) -> str:
    """
    Modify HTML by adding a PDF download link to the footer.

    :param html: The original HTML content.
    :param href: The URL of the PDF file to be downloaded.
    :return: The modified HTML with the added PDF download link.
    """
    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Create a <small> wrapper
    sm_wrapper = soup.new_tag("small")

    # Create an <a> tag for the PDF download link
    a = soup.new_tag("a", href=href, title="PDF Export", download=href)
    a["class"] = "pdf-download"
    a.string = "Download PDF"

    # Append the <a> tag to the <small> wrapper
    sm_wrapper.append(a)

    # Insert the <small> wrapper at the beginning of the footer in the <body>
    soup.body.footer.insert(0, sm_wrapper)

    # Return the prettified modified HTML
    return soup.prettify()
