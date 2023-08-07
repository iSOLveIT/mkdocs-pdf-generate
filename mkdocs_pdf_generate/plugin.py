import csv
import logging
import os
from pathlib import Path
from timeit import default_timer as timer
from typing import List

from mkdocs.config import Config
from mkdocs.plugins import BasePlugin

from . import generate_txt, generate_csv

from .options import Options
from .renderer import Renderer
from .templates.filters.url import URLFilter
from .utils import get_pdf_metadata, h1_title_tag, secure_filename


class PdfGeneratePlugin(BasePlugin):
    config_scheme = Options.config_scheme

    def __init__(self):
        self._options = None
        try:
            from mkdocs.plugins import get_plugin_logger

            self._logger = get_plugin_logger("mkdocs-pdf-generate")
            self._logger.setLevel(logging.INFO)
        except ImportError:
            get_plugin_logger = logging.getLogger("mkdocs-pdf-generate")
            self._logger = get_plugin_logger
            self._logger.setLevel(logging.INFO)
        self.renderer = None
        self.enabled = True
        self.combined = False
        self.pdf_num_files = 0
        self.txt_num_files = 0
        self.num_errors = 0
        self.total_time = 0
        self.csv_build: List[List] = []

    def on_config(self, config):
        if "enabled_if_env" in self.config:
            env_name = self.config["enabled_if_env"]
            if env_name:
                self.enabled = os.environ.get(env_name) == "1"
                if not self.enabled:
                    self._logger.info(
                        "PDF export is disabled (set environment variable {} to 1 to enable)".format(env_name)
                    )
                    return

        if self.config["debug"]:
            self._logger.info("PDF debug option is enabled.")
        if self.config["debug_target"]:
            self._logger.info("Debug Target File: {}".format(self.config["debug_target"]))

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
        site_url = (
            config.site_url
            if "site_url" in config and getattr(config, "site_url", None) is not None
            else f"http://{getattr(config, 'dev_addr.host', '127.0.0.1')}:{getattr(config, 'dev_addr.port', '8000')}"
        )
        self._options.site_url = site_url

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
        self._options.out_dest_path = dest_path

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
            self._options.body_title = h1_title_tag(output_content, dict(page.meta))

            file_name = pdf_meta.get("filename") or pdf_meta.get("title") or self._options.body_title or None

            if file_name is None:
                file_name = str(src_path).split("/")[-1].rstrip(".md")
                self._logger.error(
                    "You must provide a filename for the PDF document. The source filename is used as fallback."
                )

            doc_revision: str = pdf_meta.get("revision", False)
            if doc_revision:
                file_name = (
                    f"{file_name}_R_{doc_revision.replace('.', '_')}"
                    if isinstance(doc_revision, str)
                    else "{}_R_{}".format(file_name, str(doc_revision).replace(".", "_"))
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
                generate_txt_document = pdf_meta.get("toc_txt", False)
                if generate_txt_document:
                    if self._options.toc and self._options.toc_ordering:
                        self._logger.info(
                            f"Generating TXT TOC: {file_name}.txt, from {file_name}.pdf table of contents"
                        )
                        extra_data = dict(isCover=self._options.cover, tocTitle=self._options.toc_title)
                        # Generate TOC_TXT file
                        generate_txt.pdf_txt_toc(dest_path, file_name, extra_data)
                        # Gather CSV file data
                        if self._options.enable_csv:
                            csv_data = generate_csv.get_data(dest_path, file_name, pdf_meta, site_url)
                            self.csv_build.append(csv_data)
                        self.txt_num_files += 1
                    else:
                        self._logger.info(
                            "You must set both `toc` and `toc_numbering` to `true` to generate TXT table of contents"
                        )
                output_content = self.renderer.add_link(output_content, pdf_file)
                self.pdf_num_files += 1
            except Exception as e:
                self.num_errors += 1
                raise PDFPluginException("Error converting {}. Reason: {}".format(src_path, e))
        else:
            self._logger.info("Skipped: PDF conversion for {}".format(src_path))

        end = timer()
        self.total_time += end - start
        return output_content

    def on_post_build(self, config):
        if not self.enabled:
            return

        self._logger.info("Converting {} file(s) to PDF took {:.1f}s".format(self.pdf_num_files, self.total_time))
        self._logger.info("Converted {} PDF document's TOC to TXT".format(self.txt_num_files))

        def csv_generate(data: List[List]):
            rows: List[List] = data

            csv_file_path = Path(getattr(config, "site_dir", config["site_dir"])).joinpath("4Dversions.csv")
            if rows:
                with open(csv_file_path, mode="w") as csv_file_obj:
                    csv_writer = csv.writer(
                        csv_file_obj, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL, dialect="excel"
                    )
                    csv_writer.writerows(rows)
            return len(rows)

        if self._options.enable_csv:
            csv_entry = csv_generate(self.csv_build)
            self._logger.info("Generated '4Dversions.csv' file from {} entry(s)".format(csv_entry))
        if self.num_errors > 0:
            self._logger.error("{} conversion errors occurred (see above)".format(self.num_errors))


class PDFPluginException(Exception):
    pass
