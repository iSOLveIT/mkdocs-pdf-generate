from pathlib import Path
from urllib.parse import urlparse

from . import _FilterBase


class URLFilter(_FilterBase):
    """Finds a matching filename in some directories and returns its URL."""

    def __call__(self, pathname: str) -> str:
        if not pathname:
            return ""

        # Check for URL(eg. 'https://...')
        target_url = urlparse(pathname)
        if target_url.scheme or target_url.netloc:
            return pathname

        # Search image file in below directories:
        dirs = [
            Path(self.config["config_file_path"]).parent.resolve(),
            getattr(self.config["theme"], "custom_dir", None),
            Path(self.config["docs_dir"]),
            Path("."),
        ]

        for d in dirs:
            if not d:
                continue
            path = Path.joinpath(d, pathname).resolve()
            if path.is_file():
                return path.as_uri()
        # return path

        # not found?
        return pathname
