from mkdocs.config.base import Config


class _FilterBase:
    def __init__(self, options: object):
        self.__options = options
        self.__config = options.user_config

    @property
    def options(self):
        return self.__options

    @property
    def config(self):
        return self.__config

    def __call__(self, *args):
        raise "must be overridden"
