import os
from pathlib import Path, PosixPath, WindowsPath
import re

from weasyprint import urls
from bs4 import BeautifulSoup


# check if href is relative --
# if it is relative it *should* be an HTML that generates a PDF doc
def is_doc(href: str):
    tail = Path(href).name
    ext = Path(tail).suffix

    absurl = urls.url_is_absolute(href)
    abspath = os.path.isabs(href)
    htmlfile = ext.startswith(".html")
    relative_link = re.search(r"^\.{1,2}?[\w\-.~$&+,/:;=?@%#*]*?$", href)
    if relative_link is not None:
        return True
    if absurl or abspath or not htmlfile:
        return False

    return True


# def rel_pdf_href(href: str):
#     head, tail = os.path.split(href)
#     filename, _ = os.path.splitext(tail)
#
#     internal = href.startswith("#")
#     if not is_doc(href) or internal:
#         return href
#
#     return urls.iri_to_uri(os.path.join(head, filename + ".pdf"))


def rel_html_href(base_url: str, href: str, site_url: str):
    base_url = os.path.dirname(base_url)
    rel_url = base_url.replace("file://", "")

    internal = href.startswith("#")
    if internal or not is_doc(href):
        return href

    abs_html_href = Path(rel_url).joinpath(href).resolve()
    if isinstance(abs_html_href, PosixPath):
        abs_html_href = re.sub(
            r"^(/tmp|tmp)/(mkdocs|pages)[\w\-]+",
            site_url.rstrip("/"),
            str(abs_html_href),
        )
    elif isinstance(abs_html_href, WindowsPath):
        abs_html_href = re.sub(
            r"^[\w\-:\\]+\\+(temp|Temp)\\+(mkdocs|pages)[\w\-]+",
            site_url.rstrip("/"),
            str(abs_html_href),
        )
        abs_html_href = abs_html_href.replace("\\", "/")

    if abs_html_href:
        return urls.iri_to_uri(abs_html_href)
    return href


def abs_asset_href(href: str, base_url: str):
    if urls.url_is_absolute(href) or Path(href).is_absolute():
        return href

    return urls.iri_to_uri(urls.urljoin(base_url, href))


# makes all relative asset links absolute
def replace_asset_hrefs(soup: BeautifulSoup, base_url: str):
    for link in soup.find_all("link", href=True):
        link["href"] = abs_asset_href(link["href"], base_url)

    for asset in soup.find_all(src=True):
        asset["src"] = abs_asset_href(asset["src"], base_url)

    return soup


#
# def normalize_href(href: str, rel_url: str):
#     """
#     Method to normalize a relative href to its absolute path.
#     Example: If href = ../../index.html and rel_url = foo/bar/baz/, then we get -> foo/index.html
#
#     :param href: Relative path to a file
#     :param rel_url: Current directory to use in looking for the path to the relative file
#     :return: Absolute path to the relative file
#     """
#
#     def reduce_rel(x):
#         try:
#             i = x.index("..")
#             if i == 0:
#                 return x
#
#             del x[i]
#             del x[i - 1]
#             return reduce_rel(x)
#         except ValueError:
#             return x
#
#     rel_dir = os.path.dirname(rel_url)
#     href = str.split(os.path.join(rel_dir, href), "/")
#     href = reduce_rel(href)
#
#     return os.path.join(*href)


# def get_body_id(url: str):
#     section, _ = os.path.splitext(url)
#     return '{}:'.format(section)
