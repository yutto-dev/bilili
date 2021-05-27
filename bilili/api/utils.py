from typing import Any, Callable, TypeVar

import requests

from ..utils.console.logger import Logger
from .exceptions import MaxRetryError

T = TypeVar("T")


class MaxRetry:
    def __init__(self, max_retry: int = 2):
        self.max_retry = max_retry

    def __call__(self, connect_once: Callable[..., T]) -> Callable[..., T]:
        def connect_n_times(*args: Any, **kwargs: Any) -> T:
            retry = self.max_retry + 1
            while retry:
                try:
                    return connect_once(*args, **kwargs)
                except requests.exceptions.Timeout as e:
                    Logger.warning("抓取超时，正在尝试重新连接～")
                finally:
                    retry -= 1
            raise MaxRetryError()

        return connect_n_times
