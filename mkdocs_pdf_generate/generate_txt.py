import re
from pathlib import Path
from typing import Dict

from pypdf import PdfReader


def _make_pdf_txt_toc(destination_path: Path, filename: str, extra_data: Dict) -> str:
    separate_toc_text_n_pgnum = re.compile(r"^(\d+) (.+)$|^(\d+\.)+ (.+)$")
    pdf_filename = destination_path.joinpath(f"{filename}.pdf")

    pdf_reader: PdfReader = PdfReader(pdf_filename)

    # Get the right pages containing the TOC data
    toc_page_contents = ""
    checker = ["", 0]
    for pg_num, page in enumerate(pdf_reader.pages):
        if extra_data.get("isCover", True) and pg_num == 0:
            continue
        page_content = page.extract_text().splitlines()
        page_data = [
            pg for pg in page_content if separate_toc_text_n_pgnum.search(pg) is not None and pg not in ["", "\n"]
        ]

        if checker[0] == page_data[0] or checker[0] == page_data[1]:
            break
        if checker[1] == 0:
            toc_text = page_data[0].split(" ", maxsplit=1)
            checker[0] = toc_text[1]
            checker[1] = 1

        toc_page = "\n".join(page_data)
        toc_page_contents += f"{toc_page}\n"

    # Prepare the TOC data to enable proper formatting (Page Title - Page Num)
    toc_contents = toc_page_contents.splitlines()
    toc_title = extra_data.get("tocTitle", "Table of Contents")
    toc_title += "\n"

    # Group each item in the new_toc_content list into two separate lists
    toc_item_text = []  # list of toc text
    toc_item_pgnum = []  # list of toc pg_num

    for item in toc_contents:
        match_toc_text_n_pgnum = separate_toc_text_n_pgnum.search(item)
        if match_toc_text_n_pgnum is not None:
            match_toc_pgnum = match_toc_text_n_pgnum.groups()[0]
            match_toc_text = match_toc_text_n_pgnum.groups()[1]

            # if check_toc_text_n_pgnum.search(match_toc_pgnum) is not None
            # and check_toc_text_n_pgnum.search(match_toc_text) is not None:
            toc_item_pgnum.append(match_toc_pgnum)
            toc_item_text.append(match_toc_text)

    # Check if the length of toc_item_text is equal to the length of toc_item_pgnum
    # else raise an exception.
    if len(toc_item_text) != len(toc_item_pgnum):
        raise TXTtocFileException("Generating TXT toc file failed.")

    # Reformat TOC text and store it in the TOC.txt file
    toc_items = [f"{toc_txt}\t{toc_pgnum}" for toc_txt, toc_pgnum in zip(toc_item_text, toc_item_pgnum)]
    toc_items.insert(0, toc_title)
    return "\n".join(toc_items)


def pdf_txt_toc(destination_path: Path, filename: str, extra_data: Dict) -> None:
    """Generate a toc tree from PDF to Text file.

    Arguments:
        destination_path {Path} -- path to store TXT file.
        filename {str} -- the TXT file name.
    """

    txt_file = destination_path.joinpath(f"{filename}.txt")

    txt_file_content: str = _make_pdf_txt_toc(destination_path, filename, extra_data)
    txt_file.write_text(txt_file_content, encoding="UTF-8")


class TXTtocFileException(Exception):
    pass
