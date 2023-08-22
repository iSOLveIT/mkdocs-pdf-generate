# import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

import jinja2
from mkdocs.config.base import Config

from .filters.datetime import strftime, strptime
from .filters.url import URLFilter


class Template(object):
    """
    This class represents a template for rendering content using Jinja2.

    It extracts keywords from the `mkdocs.yml` configuration and provides methods to work with Jinja2 templates.
    """

    __KEYS = [
        "author",
        "author_logo",
        "copyright",
        "disclaimer",
        "cover_title",
        "cover_subtitle",
        "site_url",
    ]

    def __init__(self, options: object, config: Config):
        """
        Initialize the Template instance.

        :param options: An object containing options for the template.
        :param config: The MkDocs configuration.
        """
        self._options = options
        self._config = config
        self._keywords = None
        self._jinja_env = None

    @property
    def _env(self) -> jinja2.Environment:
        """
        Get the Jinja2 environment for template rendering.

        :return: The Jinja2 environment.
        """

        def generate_environment() -> jinja2.Environment:
            """
            Generate a Jinja2 template environment.

            :return: Jinja2 template environment.
            """
            base_path = Path(__file__).parent.resolve()
            template_paths = []

            custom_template_path = self._get_custom_template_path()

            if custom_template_path.is_dir():
                template_paths.append(custom_template_path)
            template_paths.append(base_path.joinpath("."))

            file_loader = jinja2.FileSystemLoader(template_paths)
            logging_undefined = jinja2.make_logging_undefined(logger=self._options.logger, base=jinja2.Undefined)
            env = jinja2.Environment(
                loader=file_loader,
                undefined=logging_undefined,
                lstrip_blocks=True,
                trim_blocks=True,
                autoescape=True,
            )

            env.filters["strptime"] = strptime
            env.filters["strftime"] = strftime
            env.filters["to_url"] = URLFilter(self._options, self._config)

            return env

        if not self._jinja_env:
            self._jinja_env = generate_environment()
        return self._jinja_env

    @property
    def keywords(self) -> Dict:
        """
        Get the keywords to pass when rendering the template.

        :return: A dictionary of keywords.
        """

        import html

        def unescape_html_in_list(values: List) -> List:
            """
            Recursively unescape HTML entities in a list of values.

            :param values: The list of values.
            :return: The list with HTML entities unescaped.
            """
            new_values = []
            for v in values:
                if isinstance(v, str):
                    new_values.append(html.unescape(v))
                elif isinstance(v, List):
                    new_values.append(unescape_html_in_list(v))
                elif isinstance(v, Dict):
                    unescape_html(v)
                    new_values.append(v)
                else:
                    new_values.append(v)
            return new_values

        def unescape_html(variables: Dict):
            """
            Recursively unescape HTML entities in a dictionary of variables.

            :param variables: The dictionary of variables.
            :type variables: dict
            """
            for k, v in variables.items():
                if isinstance(v, str):
                    variables[k] = html.unescape(v)
                elif isinstance(v, List):
                    variables[k] = unescape_html_in_list(v)
                elif isinstance(v, Dict):
                    unescape_html(v)

        def build_keywords() -> Dict[str, Any]:
            """
            Build and return a dictionary of keywords.

            :return: The dictionary of keywords.
            """
            # keywords = {}
            keywords = self._config["extra"]

            for key in self.__KEYS:
                if hasattr(self._options, key):
                    keywords[key] = getattr(self._options, key)
                elif key in self._config:
                    keywords[key] = self._config[key]

            unescape_html(keywords)

            keywords["now"] = datetime.now()

            if self._options.verbose:
                from pprint import pformat

                self._options.logger.info("Template variables:")
                for line in pformat(keywords).split("\n"):
                    self._options.logger.info("  " + line)

            return keywords

        if not self._keywords:
            self._keywords = build_keywords()

        return self._keywords

    def select(self, names: [str], parent=None, globals=None) -> jinja2.Template:
        """
        Find and load a template by names.

        :param names: A list of template names to search for.
        :param parent: The parent template.
        :param globals: Global variables to pass to the template.
        :return: The selected Jinja2 template.
        """

        real_names = []
        for name in names:
            for ext in [".html.j2", ".html.jinja2", ".html", ".htm"]:
                real_names.append(name + ext)

        return self._env.select_template(real_names, parent=parent, globals=globals)

    def _get_custom_template_path(self) -> Path:
        """
        Get the resolved custom template path.

        :return: Resolved custom template path.
        """
        docs_src_dir = Path(self._config["config_file_path"]).parent.resolve()
        custom_template_path = Path(self._options.custom_template_path)
        if not custom_template_path.is_absolute():
            custom_template_path = docs_src_dir.joinpath(self._options.custom_template_path)
        return custom_template_path
