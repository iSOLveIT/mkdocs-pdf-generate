import re
from pathlib import Path, PosixPath, WindowsPath
from typing import Dict, List, Union

from weasyprint import urls
from simple_file_checksum import get_checksum


def rel_html_href(file_path: Union[Path, str], site_url: str) -> str:
    """
    Convert a local file path to a relative HTML href.

    This function takes a local file path and a site URL, and returns a relative
    HTML href that can be used in a website.

    :param file_path: The local path to the file.
    :param site_url: The base URL of the website.
    :return: The relative HTML href for the file.
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    rel_url = file_path.as_uri()
    abs_html_href = rel_url.replace("file://", "")

    if isinstance(file_path, PosixPath):
        abs_html_href = re.sub(
            r"^(/tmp|tmp)/(mkdocs|pages)[\w\-]+|^[\w\-.~$&+,/:;=?@%#* \\]+[/\\]site",
            site_url.rstrip("/"),
            str(abs_html_href),
        )
    elif isinstance(file_path, WindowsPath):
        abs_html_href = re.sub(
            r"^[\w\-:\\]+\\+(temp|Temp)\\+(mkdocs|pages)[\w\-]+|^[\w\-.~$&+,/:;=?@%#* \\]+[/\\]site",
            site_url.rstrip("/"),
            str(abs_html_href),
        )
        abs_html_href = abs_html_href.replace("\\", "/")

    return urls.iri_to_uri(abs_html_href)


def get_data(destination_path: Path, filename: str, pdf_meta: Dict, site_url: str) -> List[str]:
    """
    Get a list of file URLs and metadata for a given PDF file.

    :param destination_path: The destination directory path.
    :param filename: The base filename (without extension) of the PDF file.
    :param pdf_meta: Metadata for the PDF file.
    :param site_url: The base URL of the website.
    :return: A list containing metadata and URLs related to the PDF file.
    """
    pdf_file = destination_path.joinpath(f"{filename}.pdf")
    txt_file = destination_path.joinpath(f"{filename}.txt")
    pdf_url = rel_html_href(pdf_file, site_url)
    txt_url = rel_html_href(txt_file, site_url)

    title = pdf_meta.get("csv_name") or filename.split("_R_")[0]
    revision = "R_{}".format(filename.split("_R_")[1])
    pdf_checksum = get_checksum(pdf_file, algorithm="MD5").upper()
    txt_checksum = get_checksum(txt_file, algorithm="MD5").upper()
    doc_type = pdf_meta.get("type", "Document")

    return [
        title.replace(" ", "_"),
        doc_type,
        revision,
        "",  # Placeholder for future use
        "",  # Placeholder for future use
        str(pdf_url),
        pdf_checksum,
        txt_checksum,
        str(txt_url),
    ]
