import re
from typing import Dict, List, Optional

import html2text
from bs4 import NavigableString, PageElement, Tag

from .options import Options
from .utils import secure_filename

remove_unwanted_str = re.compile(r"\\|`{,2}")
text_maker = html2text.HTML2Text()
text_maker.unicode_snob = True
text_maker.ignore_links = True


def make_txt_toc(soup: PageElement, options: Options, pdf_metadata: Optional[Dict] = None) -> None:
    """Generate a toc tree.

    Arguments:
        soup {BeautifulSoup} -- target element.
        options {Options} -- the project options.
    """

    file_name = pdf_metadata.get("filename") or pdf_metadata.get("title") or options.body_title or None

    if file_name is None:
        file_name = str(options.md_src_path).split("/")[-1].rstrip(".md")
        options.logger.error(
            "You must provide a filename for the TXT document. " "The source filename is used as fallback."
        )

    # Generate a secure filename
    file_name = secure_filename(file_name)

    txt_file = options.out_dest_path.joinpath(f"{file_name}.txt")

    if options.toc:
        txt_file_content = _make_txt_indexes(soup, options)
        txt_file.write_text(txt_file_content, encoding="UTF-8")


def _make_txt_indexes(soup: PageElement, options: Options) -> str:
    """Generate ordered chapter number and TOC of document.

    Arguments:
        soup {BeautifulSoup} -- DOM object of Document.
        options {Options} -- The options of this sequence.
    """

    # Step 1: (re)ordered headings
    if options.toc_ordering:
        _inject_txt_heading_order(soup, options)

    # Step 2: generate toc page
    level = options.toc_level
    if level < 1 or level > 6:
        return

    options.logger.info(f"Building TXT file containing the document's table of contents.")

    h1li = None
    h2ul = h2li = h3ul = h3li = h4ul = h4li = h5ul = h5li = h6ul = None
    # exclude_lv2 = exclude_lv3 = False

    def makeLink(h: Tag) -> Tag:
        item = soup.new_tag("p")
        if h.name == "h1":
            return item
        prefix = h.get("data-numbering", None)
        # a = soup.new_tag("p")
        if prefix is not None:
            item.append(prefix)

        for el in h.contents:
            if el.name == "a":
                item.append(el.contents[0])
            else:
                item.append(_clone_element(el))
        # li.append(a)
        return item

    toc: Tag = soup.new_tag("article", id="txt-toc")
    title = soup.new_tag("p")
    title.append(soup.new_string(options.toc_title))
    toc.append(title)

    h1ul = soup.new_tag("div")
    toc.append(h1ul)

    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    for h in headings:
        if h.name == "h1":
            h1li = makeLink(h)
            h1ul.append(h1li)
            h2ul = h2li = h3ul = h3li = h4ul = h4li = h5ul = h5li = h6ul = None

            # exclude_lv2 = _is_exclude(h.get("id", None), options)

        elif h.name == "h2" and level >= 2:
            if not h2ul:
                h2ul = soup.new_tag("div")
                h1li.append(h2ul)
            h2li = makeLink(h)
            h2ul.append(h2li)
            h3ul = h3li = h4ul = h4li = h5ul = h5li = h6ul = None

            # exclude_lv3 = _is_exclude(h.get("id", None), options)

        elif h.name == "h3" and level >= 3:
            if not h2li:
                continue
            if not h3ul:
                h3ul = soup.new_tag("div")
                h2li.append(h3ul)
            h3li = makeLink(h)
            h3ul.append(h3li)
            h4ul = h4li = h5ul = h5li = h6ul = None

        elif h.name == "h4" and level >= 4:
            if not h3li:
                continue
            if not h4ul:
                h4ul = soup.new_tag("div")
                h3li.append(h4ul)
            h4li = makeLink(h)
            h4ul.append(h4li)
            h5ul = h5li = h6ul = None

        elif h.name == "h5" and level >= 5:
            if not h4li:
                continue
            if not h5ul:
                h5ul = soup.new_tag("div")
                h4li.append(h5ul)
            h5li = makeLink(h)
            h5ul.append(h5li)
            h6ul = None

        elif h.name == "h6" and level >= 6:
            if not h5li:
                continue
            if not h6ul:
                h6ul = soup.new_tag("div")
                h5li.append(h6ul)
            h6li = makeLink(h)
            h6ul.append(h6li)

        else:
            continue
        pass

    html_str = f"""{toc}"""
    text_str = text_maker.handle(html_str)
    clean_content = remove_unwanted_str.sub("", text_str)

    def restructure_txt_content(text: str) -> str:
        txt_data: List = text.splitlines()
        new_txt_data: List = [i for i in txt_data if len(i) != 0]
        toc_title = new_txt_data.pop(0)
        toc_title += "\n"
        new_txt_data.insert(0, toc_title)
        return "\n".join(new_txt_data)

    txt_content = restructure_txt_content(clean_content)
    return txt_content


def _inject_txt_heading_order(soup: Tag, options: Options):
    level = options.toc_level
    if level < 1 or level > 6:
        return

    h2n = h3n = h4n = h5n = h6n = 0
    # exclude_lv2 = exclude_lv3 = False

    headings = soup.find_all(["h2", "h3", "h4", "h5", "h6"])
    for h in headings:
        # if h.name == "h1":
        #     h1n += 1
        #     h2n = h3n = 0
        #     prefix = ""

        # exclude_lv2 = _is_exclude(h.get("id", None), options)

        if h.name == "h2" and level >= 2:
            h2n += 1
            h3n = h4n = h5n = h6n = 0
            prefix = f"{h2n}. "

            # exclude_lv3 = _is_exclude(h.get("id", None), options)

        elif h.name == "h3" and level >= 3:
            h3n += 1
            h4n = h5n = h6n = 0
            prefix = f"{h2n}.{h3n}. "

        elif h.name == "h4" and level >= 4:
            h4n += 1
            h5n = h6n = 0
            prefix = f"{h2n}.{h3n}.{h4n}. "

        elif h.name == "h5" and level >= 5:
            h5n += 1
            h6n = 0
            prefix = f"{h2n}.{h3n}.{h4n}.{h5n}. "

        elif h.name == "h6" and level >= 6:
            h6n += 1
            prefix = f"{h2n}.{h3n}.{h4n}.{h5n}.{h6n}. "

        else:
            continue

        h["data-numbering"] = prefix


def _clone_element(el: PageElement) -> PageElement:
    if isinstance(el, NavigableString):
        return type(el)(el)

    copy = Tag(None, el.builder, el.name, el.namespace, el.nsprefix)
    # work around bug where there is no builder set
    # https://bugs.launchpad.net/beautifulsoup/+bug/1307471
    copy.attrs = dict(el.attrs)
    for attr in ("can_be_empty_element", "hidden"):
        setattr(copy, attr, getattr(el, attr))
    for child in el.contents:
        copy.append(_clone_element(child))
    return copy