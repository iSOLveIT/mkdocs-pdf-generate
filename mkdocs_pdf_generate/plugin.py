import logging
import os
from pathlib import Path
from timeit import default_timer as timer

from mkdocs.config import Config
from mkdocs.plugins import BasePlugin

from .options import Options
from .renderer import Renderer
from .templates.filters.url import URLFilter
from .utils import get_pdf_metadata, h1_title_tag, secure_filename


class PdfGeneratePlugin(BasePlugin):

    config_scheme = Options.config_scheme

    def __init__(self):
        self._options = None
        self._logger = logging.getLogger("mkdocs.pdf-generate")
        self._logger.setLevel(logging.INFO)
        self.renderer = None
        self.enabled = True
        self.combined = False
        self.num_files = 0
        self.num_errors = 0
        self.total_time = 0

    def on_config(self, config):
        if "enabled_if_env" in self.config:
            env_name = self.config["enabled_if_env"]
            if env_name:
                self.enabled = os.environ.get(env_name) == "1"
                if not self.enabled:
                    self._logger.info(
                        "PDF export is disabled (set environment variable {} to 1 to enable)".format(
                            env_name
                        )
                    )
                    return

        if self.config["debug"]:
            self._logger.info("PDF debug option is enabled.")
        if self.config["debug_target"]:
            self._logger.info(
                "Debug Target File: {}".format(self.config["debug_target"])
            )

        self._options = Options(self.config, config, self._logger)

        from weasyprint.logger import LOGGER

        if self._options.verbose:
            LOGGER.setLevel(logging.DEBUG)
            self._logger.setLevel(logging.DEBUG)
        else:
            LOGGER.setLevel(logging.ERROR)

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        LOGGER.addHandler(handler)

        self.renderer = Renderer(options=self._options)
        return config

    def on_nav(self, nav, config, files):
        if not self.enabled:
            return nav

        from .renderer import Renderer

        self.renderer = Renderer(options=self._options)

        self.renderer.pages = [None] * len(nav.pages)
        for page in nav.pages:
            self.renderer.page_order.append(page.file.url)

        return nav

    def on_post_page(self, output_content, page, config: Config):
        if not self.enabled:
            return output_content

        start = timer()

        # Since the MkDocs build is done on a local server, the `site_url` config variable is equal to
        # the address of the local server. But if we are hosting the documentation on a remote server,
        # we would want the `site_url` to be the remote server, so we need to set `site_url` variable
        # in our `mkdocs.yml` configuration file.
        # The plugin will then pick the user defined `site_url` variable and set it as the value
        # for the `site_url` under `config`.
        # We are doing this because we want the plugin to be able to determine where project links in the PDF
        # will lead to.
        site_url = [i["site_url"] for i in config.user_configs if "site_url" in i]
        if len(site_url) > 0:
            self._options.site_url = site_url[0]

        try:
            abs_dest_path = Path(page.file.abs_dest_path)
            src_path = Path(page.file.src_path)
        except AttributeError:
            # Support for mkdocs <1.0
            abs_dest_path = Path(page.abs_output_path)
            src_path = Path(page.input_path)

        self._options.md_src_path = src_path

        dest_path = abs_dest_path.parent
        if not dest_path.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)

        pdf_meta = get_pdf_metadata(page.meta)
        build_pdf_document = pdf_meta.get("build", True)

        if self._options.debug and self._options.debug_target is not None:
            # Debugging only the debug target file
            path_filter = URLFilter(self._options, self._options.user_config)
            debug_target_file = path_filter(pathname=str(self._options.debug_target))
            doc_src_path = path_filter(pathname=str(self._options.md_src_path))
            if doc_src_path == debug_target_file:
                build_pdf_document = True
            else:
                build_pdf_document = False

        if build_pdf_document:
            self._options.body_title = h1_title_tag(output_content, page.meta)

            file_name = (
                pdf_meta.get("filename")
                or pdf_meta.get("title")
                or self._options.body_title
                or None
            )

            if file_name is None:
                file_name = str(src_path).split("/")[-1].rstrip(".md")
                self._logger.error(
                    "You must provide a filename for the PDF document. "
                    "The source filename is used as fallback."
                )

            # Generate a secure filename
            file_name = secure_filename(file_name)

            base_url = dest_path.joinpath(file_name).as_uri()
            pdf_file = file_name + ".pdf"

            try:
                self._logger.info("Converting {} to {}".format(src_path, pdf_file))
                self.renderer.write_pdf(
                    output_content,
                    base_url,
                    dest_path.joinpath(pdf_file),
                    pdf_metadata=pdf_meta,
                )
                output_content = self.renderer.add_link(output_content, pdf_file)
                self.num_files += 1
            except Exception as e:
                self.num_errors += 1
                raise PDFPluginException(
                    "Error converting {} to PDF: {}".format(src_path, e)
                )
                # self._logger.error("Error converting {} to PDF: {}".format(src_path, e))
        else:
            self._logger.info("Skipped: PDF conversion for {}".format(src_path))

        end = timer()
        self.total_time += end - start
        return output_content

    def on_post_build(self, config):
        if not self.enabled:
            return

        self._logger.info(
            "Converting {} files to PDF took {:.1f}s".format(
                self.num_files, self.total_time
            )
        )
        if self.num_errors > 0:
            self._logger.error(
                "{} conversion errors occurred (see above)".format(self.num_errors)
            )


class PDFPluginException(Exception):
    pass
