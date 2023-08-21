from typing import Union

from bs4 import BeautifulSoup, NavigableString, PageElement, Tag

from .options import Options


def make_toc(soup: PageElement, options: Options):
    """
    Generate a table of contents (toc) tree if enabled in options.

    :param soup: Target BeautifulSoup PageElement.
    :param options: Project options.
    """

    if options.toc:
        _make_indexes(soup, options)


def _make_indexes(soup: BeautifulSoup, options: Options) -> None:
    """
    Generate ordered chapter numbers and Table of Contents (TOC) for the document.

    :param soup: BeautifulSoup object representing the DOM of the document.
    :param options: Options instance containing generation settings.
    """

    # Step 1: (re)ordered headings
    if options.toc_ordering:
        _inject_heading_order(soup, options)

    # Step 2: generate toc page
    level = options.toc_level
    if not (1 <= level <= 6):
        return

    options.logger.info(f"Generate table of contents up to heading level {level} for PDF document.")

    h1li = None
    h2ul = h2li = h3ul = h3li = h4ul = h4li = h5ul = h5li = h6ul = None
    # exclude_lv2 = exclude_lv3 = False

    def make_link(heading_tag: Tag) -> Tag:
        """
        Create a link for a heading and return it wrapped in an 'li' tag.

        :param heading_tag: The heading tag to create a link for.
        :return: An 'li' tag containing the link.
        """
        li = soup.new_tag("li")
        if heading_tag.name == "h1":
            return li
        ref = heading_tag.get("id", "")
        prefix = heading_tag.get("data-numbering", None)
        a = (
            soup.new_tag("a", href=f"#{ref}", attrs={"data-numbering": prefix})
            if prefix is not None
            else soup.new_tag("a", href=f"#{ref}")
        )
        for el in heading_tag.contents:
            if el.name == "a":
                a.append(el.contents[0])
            else:
                a.append(_clone_element(el))
        li.append(a)
        options.logger.debug(f"| [{heading_tag.get_text(separator=' ')}]({ref})")
        return li

    toc = soup.new_tag("article", id="doc-toc")
    title = soup.new_tag("h1")
    title.append(soup.new_string(options.toc_title))
    toc.append(title)

    h1ul = soup.new_tag("ul")
    toc.append(h1ul)

    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    for h in headings:
        if h.name == "h1":
            h1li = make_link(h)
            h1ul.append(h1li)
            h2ul = h2li = h3ul = h3li = h4ul = h4li = h5ul = h5li = h6ul = None

            # exclude_lv2 = _is_exclude(h.get("id", None), options)

        elif h.name == "h2" and level >= 2:
            if not h2ul:
                h2ul = soup.new_tag("ul")
                h1li.append(h2ul)
            h2li = make_link(h)
            h2ul.append(h2li)
            h3ul = h3li = h4ul = h4li = h5ul = h5li = h6ul = None

            # exclude_lv3 = _is_exclude(h.get("id", None), options)

        elif h.name == "h3" and level >= 3:
            if not h2li:
                continue
            if not h3ul:
                h3ul = soup.new_tag("ul")
                h2li.append(h3ul)
            h3li = make_link(h)
            h3ul.append(h3li)
            h4ul = h4li = h5ul = h5li = h6ul = None

        elif h.name == "h4" and level >= 4:
            if not h3li:
                continue
            if not h4ul:
                h4ul = soup.new_tag("ul")
                h3li.append(h4ul)
            h4li = make_link(h)
            h4ul.append(h4li)
            h5ul = h5li = h6ul = None

        elif h.name == "h5" and level >= 5:
            if not h4li:
                continue
            if not h5ul:
                h5ul = soup.new_tag("ul")
                h4li.append(h5ul)
            h5li = make_link(h)
            h5ul.append(h5li)
            h6ul = None

        elif h.name == "h6" and level >= 6:
            if not h5li:
                continue
            if not h6ul:
                h6ul = soup.new_tag("ul")
                h5li.append(h6ul)
            h6li = make_link(h)
            h6ul.append(h6li)

        else:
            continue
        pass

    soup.body.insert(0, toc)


def _inject_heading_order(soup: Tag, options: Options):
    """
    Injects numbering into headings based on their level.

    :param soup: BeautifulSoup Tag containing the parsed HTML.
    :param options: Options for heading injection.
    """
    level = options.toc_level
    if not (1 <= level <= 6):
        return

    options.logger.debug(f"Number headings up to level {level}.")

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


def _clone_element(el: Union[BeautifulSoup, PageElement]) -> Tag:
    """
    Clone a BeautifulSoup PageElement.

    This function creates a deep copy of the given PageElement while preserving its structure and attributes.

    :param el: The PageElement to be cloned.
    :return: A new PageElement that is a deep copy of the input element.
    """
    if isinstance(el, NavigableString):
        # If the element is a NavigableString, create a new instance of it.
        return type(el)(el)

    copy = Tag(None, el.builder, el.name, el.namespace, el.nsprefix)
    # Workaround for a bug where the builder is not set. (See: https://bugs.launchpad.net/beautifulsoup/+bug/1307471)
    copy.attrs = dict(el.attrs)
    # Copy attribute values.
    for attr in ("can_be_empty_element", "hidden"):
        setattr(copy, attr, getattr(el, attr))
    # Recursively clone child elements.
    for child in el.contents:
        copy.append(_clone_element(child))

    return copy
