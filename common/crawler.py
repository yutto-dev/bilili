import os
import re

import requests


class Crawler(requests.Session):

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    }

    def __init__(self):
        super().__init__()
        self.headers.update(Crawler.header)

    def set_cookies(self, cookies):
        """传入一个字典，用于设置 cookies"""

        requests.utils.add_dict_to_cookiejar(self.cookies, cookies)

    def download_bin(self, url, file_path, stream=True, chunk_size=1024, **kw):
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
            print("[warn] {} failed to download".format(file_path))
        if os.path.exists(file_path):
            with open(tmp_path, "rb") as fr:
                with open(file_path, "wb") as fw:
                    fw.write(fr.read())
            os.remove(tmp_path)
        else:
            os.rename(tmp_path, file_path)

    def download_text(self, url, file_path, **kw):
        """下载文本，以 UTF-8 编码保存文件"""

        res = self.get(url, **kw)
        res.encoding = res.apparent_encoding
        with open(file_path, 'w', encoding='utf_8') as f:
            f.write(res.text)


class BililiCrawler(Crawler):

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
        'Referer': 'https://www.bilibili.com',
    }

    def __init__(self):
        super().__init__()
        self.headers.update(BililiCrawler.header)
