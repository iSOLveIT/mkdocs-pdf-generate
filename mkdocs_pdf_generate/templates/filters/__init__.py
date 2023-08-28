from typing import Any

from mkdocs.config.defaults import MkDocsConfig


class _FilterBase:
    """
    Base class for filters in MkDocs.

    This class provides a foundation for creating custom filters in MkDocs.
    Subclasses must implement the `__call__` method.

    :param options: Options for the filter.
    :param config: MkDocs configuration.
    """

    def __init__(self, options: Any, config: MkDocsConfig):
        """
        Initialize a new FilterBase instance.

        :param options: Options for the filter.
        :param config: MkDocs configuration.
        """
        self.__options = options
        self.__config = config

    @property
    def options(self) -> Any:
        """
        Get the options for the filter.

        :return: Options for the filter.
        """
        return self.__options

    @property
    def config(self) -> MkDocsConfig:
        """
        Get the MkDocs configuration.

        :return: MkDocs configuration.
        """
        return self.__config

    def __call__(self, *args):
        """
        This method must be overridden by subclasses.

        :raise NotImplementedError: If the method is not overridden.
        """
        raise NotImplementedError("Subclasses must override this method.")
