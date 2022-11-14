import os
import random
from typing import Callable, List, Tuple, Union

import requests

from ..handlers.base import Handler
from ..utils.console.logger import Logger
from ..utils.crawler import Crawler


class RemoteFile(Handler):
    """远程文件类

    网络 url 与本地文件的绑定，可调用 download 进行下载
    download 支持断点续传
    """

    before_download: Callable[..., None]
    downloaded: Callable[..., None]
    before_update: Callable[..., None]
    updated: Callable[..., None]

    def __init__(
        self, url: str, local_path: str, mirrors: List[str] = [], range: Tuple[int, Union[int, str]] = (0, "")
    ):
        super().__init__(["before_download", "before_update", "updated", "downloaded"])
        self.url = url
        self.mirrors = mirrors
        self.path = local_path
        self.name = os.path.split(self.path)[-1]
        self.tmp_path = self.path + ".dl"
        self.size = self.get_local_size()
        self.range = range

    def get_local_size(self) -> int:
        """通过 os.path.getsize 获取本地文件大小"""
        try:
            if os.path.exists(self.tmp_path):
                size = os.path.getsize(self.tmp_path)
            elif os.path.exists(self.path):
                size = os.path.getsize(self.path)
            else:
                size = 0
        except FileNotFoundError:
            size = 0
        return size

    def download(self, thread_spider: Crawler, stream: bool = True, chunk_size: int = 1024):
        """[summary]

        Args:
            thread_spider (requests.Session): 线程全局下载器，由线程池管理并传入，每个线程拥有一个
            stream (bool, optional): 是否启用流式下载. Defaults to True.
            chunk_size (int, optional): 块大小. Defaults to 1024.
        """
        spider = thread_spider
        self.before_download(self)
        if not os.path.exists(self.path):
            downloaded = False
            while not downloaded:
                # 设置 headers
                headers = dict(spider.headers)
                headers["Range"] = "bytes={}-{}".format(self.size + self.range[0], self.range[1])
                url = random.choice([self.url] + self.mirrors) if self.mirrors else self.url

                try:
                    # 尝试建立连接
                    res = spider.get(url, stream=stream, headers=headers, timeout=(5, 10))
                    # 下载到临时路径
                    with open(self.tmp_path, "ab") as f:
                        if stream:
                            for chunk in res.iter_content(chunk_size=chunk_size):
                                if not chunk:
                                    break
                                self.before_update(self)
                                f.write(chunk)
                                self.size += len(chunk)
                                self.updated(self)
                        else:
                            f.write(res.content)
                    # size 检验，因为有时明明没下完仍然会停止下载
                    if self.range[1] and (self.range[1] - self.range[0] + 1 != self.size):
                        downloaded = False
                    else:
                        downloaded = True
                except requests.exceptions.RequestException:
                    Logger.warning("文件 {} 下载超时，正在重试...".format(self.name))

            # 从临时文件迁移，并删除临时文件
            if os.path.exists(self.path):
                os.remove(self.path)
            os.rename(self.tmp_path, self.path)

        self.downloaded(self)
