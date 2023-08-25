import logging
from pathlib import Path
from typing import Dict

from mkdocs.config import config_options
from mkdocs.config.base import LegacyConfig
from mkdocs.config.defaults import MkDocsConfig


from .templates.filters.url import URLFilter
from .templates.template import Template


class Options(object):
    DEFAULT_MEDIA_TYPE = "print"

    config_scheme = (
        ("media_type", config_options.Type(str, default=DEFAULT_MEDIA_TYPE)),
        ("verbose", config_options.Type(bool, default=False)),
        ("enable_csv", config_options.Type(bool, default=False)),
        ("debug", config_options.Type(bool, default=False)),
        ("debug_target", config_options.Type(str, default="")),
        ("enabled_if_env", config_options.Type(str)),
        ("theme_handler_path", config_options.Type(str)),
        ("author", config_options.Type(str, default=None)),
        ("author_logo", config_options.Type(str, default=None)),
        ("copyright", config_options.Type(str, default=None)),
        ("disclaimer", config_options.Type(str, default=None)),
        ("include_legal_terms", config_options.Type(bool, default=False)),
        ("cover", config_options.Type(bool, default=True)),
        ("cover_title", config_options.Type(str, default=None)),
        ("cover_subtitle", config_options.Type(str, default=None)),
        ("custom_template_path", config_options.Type(str, default="templates")),
        ("toc", config_options.Type(bool, default=True)),
        ("toc_numbering", config_options.Type(bool, default=True)),
        ("toc_title", config_options.Type(str, default="Table of Contents")),
        ("toc_level", config_options.Type(int, default=4)),
        ("cover_images", config_options.Type(dict, default=None)),
    )

    def __init__(self, local_config: LegacyConfig, config: MkDocsConfig, logger: logging):
        self.strict = True if config["strict"] else False
        self.verbose = local_config["verbose"]
        self.enable_csv = local_config["enable_csv"]
        self.debug = local_config["debug"]
        self.debug_target = None if len(local_config["debug_target"]) == 0 else local_config["debug_target"]
        self._src_path = None
        self._dest_path = None

        # user_configs in mkdocs.yml
        self._user_config: MkDocsConfig = config
        self._site_url = config["site_url"]

        # Author and Copyright
        self._author = local_config["author"]
        if not self._author:
            self._author = config["site_author"]

        self._copyright = local_config["copyright"]
        if not self._copyright:
            self._copyright = config["copyright"]

        self._disclaimer = local_config["disclaimer"]
        self._include_legal_terms = local_config["include_legal_terms"]

        # Individual document type cover
        self._cover_images: Dict = local_config["cover_images"]

        # Cover
        self.cover = local_config["cover"]
        self._cover_title = local_config["cover_title"] if local_config["cover_title"] else config["site_name"]
        self._cover_subtitle = local_config["cover_subtitle"]

        # path to custom template 'cover.html' and 'custom.css'
        self.custom_template_path = local_config["custom_template_path"]

        # TOC and Chapter heading
        self.toc = local_config["toc"]
        self.toc_title = local_config["toc_title"]
        self.toc_level = local_config["toc_level"]
        self.toc_ordering = local_config["toc_numbering"]

        # H1 Title of the document
        self._body_title: str = ""

        # Theme and theme handler
        self.theme_name = config["theme"].name
        self.theme_handler_path = local_config.get("theme_handler_path", None)
        if not self.theme_handler_path:
            # Read from global config only if plugin config is not set
            self.theme_handler_path = config.get("theme_handler_path", None)

        # Template handler(Jinja2 wrapper)
        self._template = Template(self, config)

        # Author Logo
        logo_path_filter = URLFilter(self, config)
        self.author_logo = local_config["author_logo"]
        if not self.author_logo:
            config_theme = config["theme"]
            self.author_logo = config_theme["logo"]
        if isinstance(self.author_logo, str):
            self.author_logo = logo_path_filter(self.author_logo)

        # for system
        self._logger = logger

    @property
    def site_url(self) -> str:
        return self._site_url

    @site_url.setter
    def site_url(self, url: str):
        self._site_url = url

    @property
    def body_title(self) -> str:
        return self._body_title

    @body_title.setter
    def body_title(self, text: str):
        self._body_title = text

    @property
    def author(self) -> str:
        return self._author

    @property
    def copyright(self) -> str:
        return self._copyright

    @property
    def disclaimer(self) -> str:
        return self._disclaimer

    @property
    def include_legal_terms(self) -> bool:
        return self._include_legal_terms

    @property
    def cover_title(self) -> str:
        return self._cover_title

    @property
    def cover_subtitle(self) -> str:
        return self._cover_subtitle

    @property
    def user_config(self) -> MkDocsConfig:
        return self._user_config

    @property
    def cover_images(self) -> Dict:
        return self._cover_images

    @property
    def logger(self) -> logging:
        return self._logger

    @property
    def template(self) -> Template:
        return self._template

    @property
    def md_src_path(self) -> Path:
        return self._src_path

    @md_src_path.setter
    def md_src_path(self, input_path: str):
        self._src_path = input_path

    @property
    def out_dest_path(self) -> Path:
        return self._dest_path

    @out_dest_path.setter
    def out_dest_path(self, input_path: str):
        self._dest_path = input_path

    def debug_dir(self) -> Path:
        if self.debug:
            docs_src_dir = Path(self.user_config["config_file_path"]).parent.resolve()
            debug_folder_path = docs_src_dir.joinpath("pdf_html_debug")
            if not debug_folder_path.is_dir():
                debug_folder_path.mkdir(parents=True, exist_ok=True)
            return debug_folder_path
