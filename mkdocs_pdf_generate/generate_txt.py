import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from PyPDF2 import PdfReader


def get_toc_page_nums(pdf_content) -> List[int]:
    """
    Function to fetch the page number of a page that contains a TOC section.

    :param pdf_content: pdf file content
    :return: list containing start and end page numbers
    """
    checker = ["", 0]
    fetch_pg_nums = []
    for pg_num, page in enumerate(pdf_content):
        if pg_num == 0:
            continue
        page_content = page.extract_text().splitlines()
        page_data = [pg for pg in page_content if len(pg) != 0]
        if checker[0] == page_data[2] or checker[0] == page_data[1]:
            fetch_pg_nums.append(pg_num)
            break
        if checker[1] == 0:
            checker[0] = page_data[1]
            checker[1] = 1
            fetch_pg_nums.append(pg_num)
    return fetch_pg_nums


def _make_pdf_txt_toc(destination_path: Path, filename: str, extra_data: Dict) -> str:
    pdf_filename = destination_path.joinpath(f"{filename}.pdf")

    pdf_reader: PdfReader = PdfReader(pdf_filename)
    pdf_pages = pdf_reader.pages
    separate_toc_text_n_pgnum = re.compile(r"^(\d+) (.+)$|^(\d+\.)+ (.+)$")

    # Get the right pages containing the TOC data using the page numbers
    toc_pg_nums: List[int] = []
    checker = ["", 0]
    for pg_num, page in enumerate(pdf_pages):
        if extra_data.get("isCover", True) and pg_num == 0:
            continue
        page_content = page.extract_text().splitlines()
        page_data = [
            pg 
            for pg in page_content 
            if separate_toc_text_n_pgnum.search(pg) is not None and pg not in ["", "\n"]
        ]

        if checker[0] == page_data[0] or checker[0] == page_data[1]:
            toc_pg_nums.append(pg_num)
            break
        if checker[1] == 0:
            toc_text = page_data[0].split(" ", maxsplit=1)
            checker[0] = toc_text[1]
            checker[1] = 1
            toc_pg_nums.append(pg_num)

    toc_page_contents = []
    for i in range(toc_pg_nums[0], toc_pg_nums[1]):
        new_page = pdf_reader.pages[int(i)]
        new_page_data = new_page.extract_text()
        toc_page_contents.append(new_page_data)

    # Prepare the TOC data to enable proper formatting (Page Title - Page Num)
    toc_contents = "\n".join(toc_page_contents)
    toc_content = toc_contents.splitlines()
    new_toc_content = [
        i 
        for i in toc_content 
        if separate_toc_text_n_pgnum.search(i) is not None and i not in ["", "\n"]
        ]
    toc_title = extra_data.get("tocTitle", "table of Contents")
    toc_title += "\n"

    # # Run check to see if a content is TOC text or TOC page number
    # check_toc_text_n_pgnum = re.compile(r"^((\d+\.)+)|^\d+$")
    # Group each item in the new_toc_content list into two separate lists
    toc_item_text = []      # list of toc text
    toc_item_pgnum = []     # list of toc pg_num

    for item in new_toc_content:
        match_toc_text_n_pgnum = separate_toc_text_n_pgnum.search(item)
        if match_toc_text_n_pgnum is not None:
            match_toc_pgnum = match_toc_text_n_pgnum.groups()[0]
            match_toc_text = match_toc_text_n_pgnum.groups()[1]

            # if check_toc_text_n_pgnum.search(match_toc_pgnum) is not None and check_toc_text_n_pgnum.search(match_toc_text) is not None:
            toc_item_pgnum.append(match_toc_pgnum)
            toc_item_text.append(match_toc_text)
        continue

    # # Group the new_txt_data list into two separate lists using their even or odd index
    # toc_item_text = toc_data[
    #     ::2
    # ]  # the even_list contains all the elements of the original list at even indices (starting from index 0),
    # toc_item_pgnum = toc_data[
    #     1::2
    # ]  # the odd_list contains all the elements of the original list at odd indices (starting from index 1)

    # Check if the length of toc_item_text is equal to the length of toc_item_pgnum
    # else raise an exception.
    if len(toc_item_text) != len(toc_item_pgnum):
        raise TXTtocFileException("Generating TXT toc file failed.")

    # Reformat TOC text and store it in the TOC.txt file
    toc_items = [f"{txt}\t{pgnum}" for txt, pgnum in zip(toc_item_text, toc_item_pgnum)]
    toc_items.insert(0, toc_title)
    return "\n".join(toc_items)


def pdf_txt_toc(destination_path: Path, filename: str, extra_data: Dict) -> None:
    """Generate a toc tree from PDF to Text file.

    Arguments:
        destination_path {Path} -- path to store TXT file.
        filename {str} -- the TXT file name.
    """

    txt_file = destination_path.joinpath(f"{filename}.txt")

    txt_file_content = _make_pdf_txt_toc(destination_path, filename, extra_data)
    txt_file.write_text(txt_file_content, encoding="UTF-8")


class TXTtocFileException(Exception):
    pass
