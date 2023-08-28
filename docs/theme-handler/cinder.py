from bs4 import BeautifulSoup


def get_stylesheet() -> str:
    return """
    body > .container {
        margin-top: -100px;
    }

    @page {
        @bottom-left {
            content: counter(__pgnum__);
        }
        size: letter;
    }
    
    @media print {
        .noprint {
            display: none;
        }
    }
    """


def modify_html(html: str, href: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    sm_wrapper = soup.new_tag("small")

    a = soup.new_tag("a", href=href, title="PDF Export", download=None)
    a["class"] = "pdf-download"
    a.string = "Download PDF"

    sm_wrapper.append(a)
    soup.body.footer.insert(0, sm_wrapper)

    return soup.prettify()
