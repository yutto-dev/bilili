import os
import re
import time
import math
import requests

from common.base import Task, size_format, get_string_width
from common.crawler import BililiCrawler
from common.thread import ThreadPool


class Status():

    INITIALIZED = 1
    DOWNLOADING = 2
    DONE = 4

    def __init__(self):
        self.value = Status.INITIALIZED

    def switch(self, status=None):
        """ 切换到某一状态，默认为下一状态 """
        if status is None:
            self.value <<= 1
        else:
            self.value = status

    @property
    def initialized(self):
        """ 返回状态字段是否是 INITIALIZED """
        return self.value == Status.INITIALIZED

    @property
    def downloading(self):
        """ 返回状态字段是否是 DOWNLOADING """
        return self.value == Status.DOWNLOADING

    @property
    def done(self):
        """ 返回状态字段是否是 DONE """
        return self.value == Status.DONE


class BililiContainer():
    """ bilibili 影音容器类
    同时包含视频与音频
    """

    def __init__(self, id, name, path, meta, segmentation=True,
                 block_size=10*1024*1024, overwrite=False, spider=BililiCrawler()):

        self.id = id
        self.name = name
        self.path = path
        self.meta = meta
        self.segmentation = segmentation
        self.block_size = block_size
        self.overwrite = overwrite
        self.spider = spider

        self.video = None
        self.audio = None
        self.total = 0
        self.status = Status()

    def __str__(self):
        """ 视频返回的字符串 """
        num_block = len(self.video.blocks) + len(self.audio.blocks)
        return "{} qn:{} {},{}".format(self.name, self.video.qn, num_block)

    def set_video(self, **kwargs):
        self.video = BililiVideo(container=self, **kwargs)

    def set_audio(self, **kwargs):
        self.audio = BililiAudio(container=self, **kwargs)

    @property
    def medias(self):
        return (self.video, self.audio)

    @property
    def size(self):
        """ 获取本地文件大小 """
        return self.audio.size + self.video.size

    def merge(self, ffmpeg):
        ffmpeg.join_video_audio(self.video.path, self.audio.path, self.path)

        # 清除合并完成的视频片段
        os.remove(self.video.path)
        os.remove(self.audio.path)


class BililiMedia():
    """ bilibili 媒体类（视频或音频）
    """

    def __init__(self, type, url, qn, container):

        self.type = type
        self.qn = qn
        self.url = url

        self.container = container
        self.path = '{}_{}.m4s'.format(
            os.path.splitext(self.container.path)[0], self.type)
        self.name = os.path.split(self.path)[-1]
        self._get_head()
        self.container.total += self.total

        self.status = Status()
        self.blocks = []
        self._segmentation()

    def _segmentation(self):
        """ 分段，将各个片段添加至 self.blocks """
        if self.segmentation:
            for i in range(math.ceil(self.total/self.container.block_size)):
                block = BililiBlock(self, i)
                self.blocks.append(block)
        else:
            block = BililiBlock(self, 0)
            self.blocks.append(block)

    def _get_head(self):
        res = self.container.spider.head(self.url, headers={'Range': 'bytes=0-4'})
        if res.headers.get('Content-Range'):
            self.total = int(res.headers['Content-Range'].split('/')[-1])
            self.segmentation = self.container.segmentation
        elif res.headers.get('Content-Length'):
            self.total = int(res.headers['Content-Length'])
            self.segmentation = False
        else:
            self.total = None
            self.segmentation = False

    @property
    def size(self):
        """ 获取本地文件大小 """
        if self.status.done:
            return self.total
        else:
            return sum([block.size for block in self.blocks])

    def merge(self):
        """ 合并各个片段 """
        with open(self.path, "wb") as fw:
            for block in self.blocks:
                with open(block.path, "rb") as fr:
                    fw.write(fr.read())
                block.remove()


class BililiVideo(BililiMedia):
    """ bilibili 纯视频类"""

    def __init__(self, *args, **kwargs):

        super().__init__(type='video', *args, **kwargs)


class BililiAudio(BililiMedia):
    """ bilibili 纯音频类"""

    def __init__(self, *args, **kwargs):

        super().__init__(type='audio', *args, **kwargs)


class BililiBlock():
    """ bilibili 视频块类
    属性
        file: 片段所在的文件类
        path: 片段的本地存储路径
        name: 片段的名称
        tmp_path: 片段的临时文件存储路径
        id: 片段在一个文件中的唯一标志号
        size: 本地已下载部分大小
    """

    def __init__(self, media, id):

        self.media = media
        self.container = self.media.container

        self.path = "{}.{:06}".format(self.media.path, id)
        self.name = os.path.split(self.path)[-1]
        self.tmp_path = self.path + "t"
        self.id = id

        self.status = Status()
        self.size = 0

    def download(self, ffmpeg, stream=True, chunk_size=1024):
        # 更改状态
        self.status.switch()
        if self.container.status.initialized:
            self.container.status.switch()
        if self.media.status.initialized:
            self.media.status.switch()

        # 判断是否需要删除
        if self.container.overwrite:
            self.remove()
        self.size = self.get_size()
        if not os.path.exists(self.path):
            downloaded = False
            while not downloaded:
                # 设置 headers
                headers = dict(self.container.spider.headers)
                if self.media.segmentation:
                    headers["Range"] = "bytes={}-{}".format(
                        self.id * self.container.block_size + self.size,
                        (self.id+1) * self.container.block_size - 1)
                else:
                    headers["Range"] = "bytes={}-".format(
                        self.id * self.container.block_size + self.size)

                try:
                    # 尝试建立连接
                    res = self.container.spider.get(
                        self.media.url, stream=stream, headers=headers, timeout=(5, 10))
                    # 下载到临时路径
                    with open(self.tmp_path, 'ab') as f:
                        if stream:
                            for chunk in res.iter_content(chunk_size=chunk_size):
                                if not chunk:
                                    break
                                f.write(chunk)
                                self.size += len(chunk)
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
        self.status.switch()

        # 检查是否所有片段均已下载完成，如果是则合并
        if all([block.status.done for block in self.media.blocks]):
            self.media.merge()
            self.media.status.switch()

            if self.container.audio.status.done and self.container.video.status.done:
                self.container.merge(ffmpeg)
                self.container.status.switch()

    def remove(self):
        """ 删除文件及其临时文件 """
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)
        elif os.path.exists(self.path):
            os.remove(self.path)

    def get_size(self):
        """ 通过 os.path.getsize 获取片段大小 """
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


class BiliFileManager():
    """ bilibili 文件管理器

    负责资源的分发与文件监控

    属性
        files: 待管理文件 List
        pool: 线程池
        overwrite: 是否强制覆盖，默认不强制覆盖
        spider: 爬虫会话，requests.Session() 的封装
        block_size: 片段大小，单位为字节
    """

    def __init__(self, num_thread, block_size, ffmpeg, overwrite=False):
        self.ffmpeg = ffmpeg
        self.containers = []
        self.pool = ThreadPool(num_thread)
        self.overwrite = overwrite
        self.block_size = block_size

    def dispense_resources(self, resources, log=True):
        """ 资源分发，将资源切分为片段，并分发至线程池 """

        for i, container in enumerate(resources):
            print("dispenser resources {}/{}".format(i, len(resources)), end="\r")
            if os.path.exists(container.path) and not self.overwrite:
                sign = "!"
            else:
                sign = ">"
                self.containers.append(container)
                for media in container.medias:
                    if os.path.exists(media.path) and not self.overwrite:
                        media.status.switch(Status.DONE)
                        continue
                    for block in media.blocks:
                        task = Task(block.download, args=(self.ffmpeg, ))
                        self.pool.add_task(task)
            if log:
                print("------{} {}".format(sign, container.name))

    def run(self):
        """ 启动任务 """
        self.pool.run()

    def monitoring(self):
        """ 启动监控器 """
        containers = self.containers
        size, t = sum([container.size for container in containers]), time.time()
        total_size = sum([container.total for container in containers])
        center_placeholder = "%(center)s"
        while len(containers):
            bar_length = 50
            max_length = 80
            log_string = " Downloading... ".center(max_length, "=") + "\n"

            # 下载速度
            now_size, now_t = sum(
                [container.size for container in containers]), time.time()
            delta_size, delta_t = now_size - size, now_t - t
            size, t = now_size, now_t
            if delta_t < 1e-6:
                delta_t = 1e-6
            speed = delta_size / delta_t

            # 单个下载进度
            for container in containers:
                if container.status.downloading:
                    num_media_done = sum(
                        [media.status.done for media in container.medias])
                    num_media = len(container.medias)
                    line = "{}({}/{}) qn:{} {} {}/{}".format(
                        container.name,
                        num_media_done,
                        num_media,
                        container.video.qn,
                        center_placeholder,
                        size_format(container.size),
                        size_format(container.total))
                    line = line.replace(center_placeholder, max(
                        max_length-get_string_width(line)+len(center_placeholder), 0)*"-")
                    log_string += line + "\n"

            # 下载进度
            len_done = bar_length * size // total_size
            len_undone = bar_length - len_done
            log_string += '{}{} {}/{} {:12}'.format(
                "#" * len_done,
                "_" * len_undone,
                size_format(size),
                size_format(total_size),
                size_format(speed)+"/s")

            # 清空控制台并打印新的 log
            os.system('cls' if os.name == 'nt' else 'clear')
            print(log_string)

            # 监控是否全部完成
            if all([container.status.done for container in containers]):
                break

            try:
                time.sleep(max(1-(time.time()-now_t), 0.01))
            except (SystemExit, KeyboardInterrupt):
                raise

        # 清空控制台
        os.system('cls' if os.name == 'nt' else 'clear')
