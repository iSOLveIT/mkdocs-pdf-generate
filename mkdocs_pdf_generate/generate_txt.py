import re
from pathlib import Path
from typing import Dict, List, Optional, Union

import pdftotext


def _make_pdf_txt_toc(destination_path: Path, filename: str) -> str:
    pdf_filename = destination_path.joinpath(f"{filename}.pdf")
    with open(pdf_filename, "rb") as file_obj:
        pdf = pdftotext.PDF(file_obj)

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
            page_content = page.splitlines()
            page_data = [pg for pg in page_content if len(pg) != 0]
            if checker[0] == page_data[2] or checker[0] == page_data[1]:
                fetch_pg_nums.append(pg_num)
                break
            if checker[1] == 0:
                checker[0] = page_data[1]
                checker[1] = 1
                fetch_pg_nums.append(pg_num)
        return fetch_pg_nums

    # Get the right pages containing the TOC data using the page numbers
    toc_pg_nums: List[int] = get_toc_page_nums(pdf)
    toc_page_contents = []
    for i in range(toc_pg_nums[0], toc_pg_nums[1]):
        toc_page_contents.append(pdf[i])

    # Prepare the TOC data to enable proper formatting (Page Title - Page Num)
    toc_contents = "\n".join(toc_page_contents)
    toc_content = toc_contents.splitlines()
    new_toc_content = [i for i in toc_content if len(i) != 0]
    toc_title = new_toc_content.pop(0)
    toc_title += "\n"

    # Run check to see if a content is TOC text or TOC page number
    check_toc_text_n_pgnum = re.compile(r"^((\d+\.)+)|^\d+$")
    toc_data = [content for content in new_toc_content if check_toc_text_n_pgnum.search(content)]

    # Group the new_txt_data list into two separate lists using their even or odd index
    toc_item_text = toc_data[
        ::2
    ]  # the even_list contains all the elements of the original list at even indices (starting from index 0),
    toc_item_pgnum = toc_data[
        1::2
    ]  # the odd_list contains all the elements of the original list at odd indices (starting from index 1)

    # Check if the length of toc_item_text is equal to the length of toc_item_pgnum
    # else raise an exception.
    if len(toc_item_text) != len(toc_item_pgnum):
        raise TXTtocFileException("Generating TXT toc file failed.")

    # Reformat TOC text and store it in the TOC.txt file
    toc_items = [f"{txt}\t{pgnum}" for txt, pgnum in zip(toc_item_text, toc_item_pgnum)]
    toc_items.insert(0, toc_title)
    return "\n".join(toc_items)


def pdf_txt_toc(destination_path: Path, filename: str) -> None:
    """Generate a toc tree from PDF to Text file.

    Arguments:
        destination_path {Path} -- path to store TXT file.
        filename {str} -- the TXT file name.
    """

    txt_file = destination_path.joinpath(f"{filename}.txt")

    txt_file_content = _make_pdf_txt_toc(destination_path, filename)
    txt_file.write_text(txt_file_content, encoding="UTF-8")


class TXTtocFileException(Exception):
    pass
