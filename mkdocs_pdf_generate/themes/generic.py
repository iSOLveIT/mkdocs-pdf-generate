from typing import Optional

from bs4 import BeautifulSoup


def get_stylesheet() -> Optional[str]:
    return None


def modify_html(html: str, href: str) -> str:
    soup = BeautifulSoup(html, "html5lib")

    if soup.head:
        link = soup.new_tag(
            "link",
            href=href,
            rel="alternate",
            title="PDF Export",
            type="application/pdf",
        )
        soup.head.append(link)

    return str(soup)
