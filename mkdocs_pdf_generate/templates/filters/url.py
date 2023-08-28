from pathlib import Path
from urllib.parse import urlparse

from . import _FilterBase


class URLFilter(_FilterBase):
    """Filter that finds a matching filename in specified directories and returns its URL.

    This filter takes a pathname and checks whether it is a URL or a local path to a file. If it's a URL, the
    original pathname is returned. If it's a local path, the filter searches for the file in a list of directories
    and returns the URL of the first matching file found.
    """

    def __call__(self, pathname: str) -> str:
        """
        Filter the input pathname and return the corresponding URL.

        :param pathname: The input pathname to be filtered.
        :return: The URL corresponding to the input pathname.
        """
        if not pathname:
            return ""

        # Check if the pathname is already a URL
        target_url = urlparse(pathname)
        if target_url.scheme or target_url.netloc:
            return pathname

        # Search for the image file in the specified directories
        dirs = [
            Path(self.config["config_file_path"]).parent.resolve(),
            getattr(self.config["theme"], "custom_dir", None),
            Path(self.config["docs_dir"]),
            Path("."),
        ]

        for d in dirs:
            if not d:
                continue
            path = Path(d).joinpath(pathname).resolve()
            if path.is_file():
                return path.as_uri()
        
        # If not found, return the original pathname
        return pathname
