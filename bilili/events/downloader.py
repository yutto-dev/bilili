import os
import requests


noop = lambda *args, **kwargs: None


class RemoteFile():
    """ 远程文件类

    网络 url 与本地文件的绑定，可调用 download 进行下载
    download 支持断点续传
    通过中间件与外部监控程序通讯
    """

    def __init__(self, url, local_path):
        self.url = url
        self.path = local_path
        self.name = os.path.split(self.path)[-1]
        self.tmp_path = self.path + '.dl'
        self.size = self.get_local_size()
        self.events = [
            'before_download', 'before_update',
            'updated', 'downloaded'
        ]
        for event in self.events:
            setattr(self, event, noop)

    def get_local_size(self):
        """ 通过 os.path.getsize 获取本地文件大小 """
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

    def download(self, spider, stream=True, chunk_size=1024):

        self.before_download(self)
        if not os.path.exists(self.path):
            downloaded = False
            while not downloaded:
                # 设置 headers
                headers = dict(spider.headers)
                headers["Range"] = "bytes={}-".format(self.size)

                try:
                    # 尝试建立连接
                    res = spider.get(self.url, stream=stream, headers=headers, timeout=(5, 10))
                    # 下载到临时路径
                    with open(self.tmp_path, 'ab') as f:
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
                    downloaded = True
                except requests.exceptions.RequestException:
                    print(
                        "[warn] file {}, request timeout, trying again...".format(self.name))

            # 从临时文件迁移，并删除临时文件
            if os.path.exists(self.path):
                os.remove(self.path)
            os.rename(self.tmp_path, self.path)

        self.downloaded(self)

    def on(self, event, **params):
        assert event in self.events
        def on_event(func):
            def new_func(*args, **kwargs):
                return func(*args, **kwargs, **params)
            setattr(self, event, new_func)
        return on_event
