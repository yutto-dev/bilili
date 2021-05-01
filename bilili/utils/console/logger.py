from typing import Any

from ..functiontools.singleton import Singleton
from .colorful import colored_string

LOGGER_DEBUG = False


def set_logger_debug():
    global LOGGER_DEBUG
    LOGGER_DEBUG = True


class Logger(metaclass=Singleton):
    @classmethod
    def warning(cls, string: Any, *print_args, **print_kwargs):
        prefix = colored_string(" WARN ", fore="black", back="yellow")
        print(prefix + " " + str(string), *print_args, **print_kwargs)

    @classmethod
    def error(cls, string: Any, *print_args, **print_kwargs):
        prefix = colored_string(" ERROR ", fore="white", back="red")
        print(prefix + " " + str(string), *print_args, **print_kwargs)

    @classmethod
    def info(cls, string: Any, *print_args, **print_kwargs):
        prefix = colored_string(" INFO ", fore="black", back="green")
        print(prefix + " " + str(string), *print_args, **print_kwargs)

    @classmethod
    def debug(cls, string: Any, *print_args, **print_kwargs):
        if not LOGGER_DEBUG:
            return
        prefix = colored_string(" DEBUG ", fore="black", back="blue")
        print(prefix + " " + str(string), *print_args, **print_kwargs)

    @classmethod
    def print(cls, string: Any, *print_args, **print_kwargs):
        print(string, *print_args, **print_kwargs)
