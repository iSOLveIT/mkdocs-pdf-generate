import os
import re
from pathlib import Path, PosixPath, WindowsPath

from bs4 import BeautifulSoup
from weasyprint import urls


# check if href is relative, if it is relative then it *should* be an HTML that generates a PDF doc
def is_doc(href: str) -> bool:
    """
    Check if the given href is a relative link.

    :param href: The URL or path to be checked.
    :return: True if the href is a relative link, False otherwise.
    """
    tail = Path(href).name
    ext = Path(tail).suffix

    abs_url = urls.url_is_absolute(href)  # Check if it's an absolute URL
    abs_path = os.path.isabs(href)  # Check if it's an absolute path
    html_file = ext.startswith(".html")  # Check if the extension is .html

    # Check if the href matches a relative link pattern
    relative_link = re.search(r"^\.{,2}?[\w\-.~$&+,/:;=?@%#*]*?$", href)
    # If it doesn't match the relative link pattern or doesn't meet other conditions, it's not a relative link
    if not relative_link or abs_url or abs_path or not html_file:
        return False

    return True


def rel_html_href(base_url: str, href: str, site_url: str) -> str:
    """
    Resolves relative HTML href to absolute URL based on base_url and site_url.

    :param base_url: The base URL of the current HTML file.
    :param href: The relative or absolute href to be resolved.
    :param site_url: The root URL of the website.

    :return: The resolved absolute URL.
    """
    # Extract the directory portion of base_url
    new_base_url = os.path.dirname(base_url)
    rel_url = new_base_url.replace("file://", "")

    # Check if href is internal link or starts with "http://" or "https://"
    internal = href.startswith("#")
    web_url = re.search(r"^(https://|http://)", href)
    # Check if href is a document link
    is_document = is_doc(href)

    # Return href if it's a web URL or is an internal link or not a document link
    if web_url or internal or not is_document:
        return href

    # Resolve relative URL using base_url and site_url
    abs_html_href = Path(rel_url).joinpath(href).resolve()

    if isinstance(abs_html_href, PosixPath):
        abs_html_href = re.sub(
            r"^(/tmp|tmp)/(mkdocs|pages)[\w\-]+|^[\w\-.~$&+,/:;=?@%#* \\]+[/\\]site",
            site_url.rstrip("/"),
            str(abs_html_href),
        )
    elif isinstance(abs_html_href, WindowsPath):
        abs_html_href = re.sub(
            r"^[\w\-:\\]+\\+(temp|Temp)\\+(mkdocs|pages)[\w\-]+|^[\w\-.~$&+,/:;=?@%#* \\]+[/\\]site",
            site_url.rstrip("/"),
            str(abs_html_href),
        )
        abs_html_href = abs_html_href.replace("\\", "/")

    if abs_html_href:
        # Convert the resolved absolute URL to a valid URI
        return urls.iri_to_uri(abs_html_href)
    return href


def abs_asset_href(href: str, base_url: str) -> str:
    """
    Create an absolute URL for a given href based on the provided base URL.

    If the href is already an absolute URL or an absolute file path,
    it is returned as is. Otherwise, it is joined with the base URL to
    create an absolute URL.

    :param href: The href to be converted to an absolute URL.
    :type href: str
    :param base_url: The base URL to be used for creating the absolute URL.
    :type base_url: str
    :return: The absolute URL.
    :rtype: str
    """
    if urls.url_is_absolute(href) or Path(href).is_absolute():
        return href
    return urls.iri_to_uri(urls.urljoin(base_url, href))


# Make all relative asset links absolute
def replace_asset_hrefs(soup: BeautifulSoup, base_url: str) -> BeautifulSoup:
    """
    Replace the href and src attributes of assets in a BeautifulSoup object with absolute URLs.

    :param soup: The BeautifulSoup object representing the HTML content.
    :param base_url: The base URL used to convert relative URLs to absolute URLs.
    :return: The modified BeautifulSoup object with replaced asset URLs.
    """
    for link in soup.find_all("link", href=True):
        link["href"] = abs_asset_href(link["href"], base_url)

    for asset in soup.find_all(src=True):
        asset["src"] = abs_asset_href(asset["src"], base_url)
    return soup
