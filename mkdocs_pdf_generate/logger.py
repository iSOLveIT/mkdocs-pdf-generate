import logging

try:
    from mkdocs.plugins import get_plugin_logger

    using_mkdocs_logger = True
except ImportError:
    using_mkdocs_logger = False
    from logging import getLogger

    get_plugin_logger = getLogger  # Define a fallback logger function


class PDFGenFormatter(logging.Formatter):
    """Custom log formatter to match the desired log format."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record into the desired format.

        :param record: The log record to be formatted.
        :returns:Formatted log message.
        """
        level = record.levelname
        message = record.getMessage()
        pkg_name = record.name

        formatted_message = f"{level:<8} -  {pkg_name}: {message}"
        return formatted_message


def get_logger(name: str = "mkdocs-pdf-generate") -> logging.Logger:
    """
    Get a logger for PDF generation.

    :param name: Name of the logger. Defaults to "mkdocs-pdf-generate".
    :return: A logger instance.
    """
    logger = get_plugin_logger(name)

    if not using_mkdocs_logger:
        handler = logging.StreamHandler()
        formatter = PDFGenFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
