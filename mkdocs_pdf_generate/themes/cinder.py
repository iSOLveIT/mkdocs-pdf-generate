from typing import Optional

from bs4 import BeautifulSoup


def get_stylesheet() -> Optional[str]:
    return None


def modify_html(html: str, href: str) -> str:
    soup = BeautifulSoup(html, "html5lib")

    sm_wrapper = soup.new_tag("small")

    a = soup.new_tag("a", href=href, title="PDF Export", download=href)
    a["class"] = "pdf-download"
    a.string = "Download PDF"

    sm_wrapper.append(a)
    soup.body.footer.insert(0, sm_wrapper)

    return str(soup)
