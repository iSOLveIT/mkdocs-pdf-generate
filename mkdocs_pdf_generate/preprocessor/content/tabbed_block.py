import re

from bs4 import BeautifulSoup


def restructure_tabbed_content(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Restructures tabbed content in an HTML document.

    This function finds tabbed content sections within the HTML document and restructures them
    by replacing the tabbed blocks with new structures and removing the tab content divs.

    :param soup: The BeautifulSoup object representing the HTML document.
    :return: The modified BeautifulSoup object with restructured tabbed content.
    """
    # Find all labels associated with tabbed content
    labels = soup.find_all("label", attrs={"for": re.compile(r"^__tabbed_[\d_]+$")})
    # Find all blocks containing tabbed content
    blocks = soup.find_all("div", attrs={"class": "tabbed-block"})
    # Find all divs containing tab content
    tab_content = soup.find_all("div", attrs={"class": "tabbed-content"})

    new_blocks = []

    # Replace class attribute of blocks and store in new_blocks list
    for div in blocks:
        div["class"] = "new_tabbed_block"
        new_blocks.append(div)

    # Insert new_blocks after corresponding labels
    for label, div in zip(labels, new_blocks):
        label.insert_after(div)

    # Remove tab content divs
    for tab_ in tab_content:
        tab_.decompose()

    return soup
