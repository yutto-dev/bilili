import os
from typing import Dict

import requests


class DownloadFailureError(Exception):
    pass


class Crawler(requests.Session):

    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_3_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
    }

    def __init__(self):
        super().__init__()
        requests.packages.urllib3.disable_warnings()
        self.headers.update(Crawler.header)
        self.verify = False

    def set_cookies(self, cookies: Dict[str, str]):
        """传入一个字典，用于设置 cookies"""

        self.cookies_dict = cookies
        requests.utils.add_dict_to_cookiejar(self.cookies, cookies)

    def download_bin(
        self, url: str, file_path: str, stream: bool = True, chunk_size: int = 1024, **kw: Dict[str, str]
    ) -> None:
        """下载二进制文件"""

        res = self.get(url, stream=stream, **kw)
        tmp_path = file_path + ".t"
        try:
            with open(tmp_path, "wb") as f:
                if stream:
                    for chunk in res.iter_content(chunk_size=chunk_size):
                        if not chunk:
                            break
                        f.write(chunk)
                else:
                    f.write(res.content)
        except:
            os.remove(tmp_path)
            raise DownloadFailureError()
        if os.path.exists(file_path):
            with open(tmp_path, "rb") as fr:
                with open(file_path, "wb") as fw:
                    fw.write(fr.read())
            os.remove(tmp_path)
        else:
            os.rename(tmp_path, file_path)

    def download_text(self, url: str, file_path: str, **kw: Dict[str, str]) -> None:
        """下载文本，以 UTF-8 编码保存文件"""

        res = self.get(url, **kw)
        res.encoding = res.apparent_encoding
        with open(file_path, "w", encoding="utf_8") as f:
            f.write(res.text)

    def clone(self):
        new_one = self.__class__()
        new_one.set_cookies(self.cookies_dict)
        new_one.trust_env = self.trust_env
        return new_one


class BililiCrawler(Crawler):

    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
        "Referer": "https://www.bilibili.com",
    }

    def __init__(self):
        super().__init__()
        self.headers.update(BililiCrawler.header)
