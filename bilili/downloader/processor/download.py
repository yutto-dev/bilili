import os
import random
import requests

from bilili.downloader.processor.base import Processor


class DownloadProcessor(Processor):

    """ 下载处理器 """

    def get_local_size(self, path, tmp_path):
        """ 通过 os.path.getsize 获取本地文件大小 """
        try:
            if os.path.exists(tmp_path):
                size = os.path.getsize(tmp_path)
            elif os.path.exists(path):
                size = os.path.getsize(path)
            else:
                size = 0
        except FileNotFoundError:
            size = 0
        return size

    def run(self, url, path, mirrors=[], range=(0, ""), stream=True, chunk_size=1024, thread_globals={}):
        spider = thread_globals.get("spider")
        path = path
        name = os.path.split(path)[-1]
        tmp_path = path + ".dl"
        size = self.get_local_size(path, tmp_path)

        if not os.path.exists(path):
            downloaded = False
            while not downloaded:
                # 设置 headers
                headers = dict(spider.headers)
                headers["Range"] = "bytes={}-{}".format(size + range[0], range[1])
                choiced_url = random.choice([url] + mirrors) if mirrors else url

                try:
                    # 尝试建立连接
                    res = spider.get(choiced_url, stream=stream, headers=headers, timeout=(5, 10))
                    # 下载到临时路径
                    with open(tmp_path, "ab") as f:
                        if stream:
                            for chunk in res.iter_content(chunk_size=chunk_size):
                                if not chunk:
                                    break
                                f.write(chunk)
                                size += len(chunk)
                                # 更新绑定文件对应的 size
                                self.file.size = size
                        else:
                            f.write(res.content)
                    downloaded = True
                except requests.exceptions.RequestException:
                    print("[WARNING] file {}, request timeout, trying again...".format(name))

            # 从临时文件迁移，并删除临时文件
            if os.path.exists(path):
                os.remove(path)
            os.rename(tmp_path, path)
