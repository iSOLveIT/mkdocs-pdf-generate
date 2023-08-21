import re
from typing import Dict, Optional

from bs4 import BeautifulSoup

from .content import restructure_tabbed_content
from .links import rel_html_href, replace_asset_hrefs
from ..options import Options
from ..utils import enable_disclaimer


# def get_combined(soup: BeautifulSoup, base_url: str, rel_url: str):
#     for id in soup.find_all(id=True):
#         id['id'] = transform_id(id['id'], rel_url)
#
#     for a in soup.find_all('a', href=True):
#         if urls.url_is_absolute(a['href']) or os.path.isabs(a['href']):
#             continue
#
#         a['href'] = transform_href(a['href'], rel_url)
#
#     soup.body['id'] = get_body_id(rel_url)
#     soup = replace_asset_hrefs(soup, base_url)
#     soup = restructure_tabbed_content(soup)
#     return soup


def get_separate(soup: BeautifulSoup, base_url: str, site_url: str):
    # transforms all relative hrefs pointing to other html docs
    # into relative html hrefs
    for a in soup.find_all("a", href=True):
        a["href"] = rel_html_href(base_url, a["href"], site_url)

    soup = replace_asset_hrefs(soup, base_url)
    soup = restructure_tabbed_content(soup)
    return soup


def get_content(soup: BeautifulSoup, options: Options, pdf_metadata: Dict):
    content = soup.find("article", attrs={"class": "md-content__inner"})
    new_content = [content]
    soup.body.clear()
    soup.body.extend(new_content)
    # Check image alignment
    all_images = soup.find_all("img", attrs={"align": re.compile(r"left|right")})
    for img in all_images:
        # Modify <img> tags
        position = img["align"]
        img["style"] = "float:{};".format(position)
        del img["align"]
    # Check table alignment
    all_table_th = soup.find_all("th", attrs={"align": re.compile(r"left|right|center")})
    for th in all_table_th:
        # Modify <th> tags
        position = th["align"]
        th["style"] = "text-align:{};".format(position)
        del th["align"]
    all_table_td = soup.find_all("td", attrs={"align": re.compile(r"left|right|center")})
    for td in all_table_td:
        # Modify <td> tags
        position = td["align"]
        td["style"] = "text-align:{};".format(position)
        del td["align"]

    # Append disclaimer HTML to content (i.e. <div class="md-content__inner">...</div>)
    is_disclaimer_enabled = options.disclaimer
    if is_disclaimer_enabled:
        soup = enable_disclaimer(soup, options, pdf_metadata)
    return soup
