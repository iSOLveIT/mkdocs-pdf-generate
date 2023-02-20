import re
from pathlib import Path, PosixPath, WindowsPath
from typing import Dict, List

from weasyprint import urls
from simple_file_checksum import get_checksum


def rel_html_href(file_path: Path, site_url: str) -> str:
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
    pdf_file = destination_path.joinpath(f"{filename}.pdf")
    txt_file = destination_path.joinpath(f"{filename}.txt")
    pdf_url = rel_html_href(pdf_file, site_url)
    txt_url = rel_html_href(txt_file, site_url)
    title = filename.split("_R_")[0]
    revision = "R_{}".format(filename.split("_R_")[1])
    pdf_checksum = get_checksum(pdf_file, algorithm="MD5").upper()
    txt_checksum = get_checksum(txt_file, algorithm="MD5").upper()
    doc_type = pdf_meta.get("type", "None")

    return [title, doc_type, revision, "", "", str(pdf_url), pdf_checksum, txt_checksum, str(txt_url)]
