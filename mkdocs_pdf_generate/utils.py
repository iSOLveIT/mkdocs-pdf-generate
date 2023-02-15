import os
import re
from typing import Dict, Optional, Union

from bs4 import BeautifulSoup, PageElement


def get_pdf_metadata(metadata):
    pdf_meta = metadata.get("pdf") if "pdf" in metadata and metadata["pdf"] is not None else {}
    return pdf_meta


def secure_filename(filename):
    r"""Pass it a filename, and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.  The filename returned is an ASCII only string
    for maximum portability.

    On Windows systems the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename(u'i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you generate random
    filename if the function returned an empty one.

    :param filename: the filename to secure
    """
    _filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
    _windows_device_files = (
        "CON",
        "AUX",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "LPT1",
        "LPT2",
        "LPT3",
        "PRN",
        "NUL",
    )

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip("._")

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if os.name == "nt" and filename and filename.split(".")[0].upper() in _windows_device_files:
        filename = "_" + filename

    return filename


def h1_title_tag(content: Union[str, PageElement], page_metadata: Dict) -> Optional[str]:
    soup = content
    if isinstance(soup, str):
        soup = BeautifulSoup(soup, "html5lib")
    title = soup.find("h1", attrs={"id": re.compile(r"[\w_\-]+")})
    if title is None:
        return page_metadata.get("title")
    title = re.sub(r"^[\d.]+ ", "", title.text)
    return title
