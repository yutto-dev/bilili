import os
import re
import time
import math
import subprocess

from bilili.events.middleware import DownloaderMiddleware
from bilili.quality import quality_map
from bilili.tools import global_middleware
from bilili.utils.base import repair_filename


class BililiContainer:
    """ bilibili 媒体容器类
    即 B 站上的单个视频，其中可能包含多个媒体单元
    * 包含多个 flv 片段
    * 包含 m4s 的视频与音频流
    * 包含完整的一个 mp4
    """

    def __init__(self, id, name, meta, type="dash", video_dir=""):

        self.id = id
        self.name = name
        self.meta = meta
        self.type = type
        self.path = os.path.join(video_dir, "{}.mp4".format(repair_filename(self.name)))

        self.medias = []
        self.quality = None
        self.height = None
        self.width = None
        self._ = DownloaderMiddleware(parent=global_middleware)

    def append_media(self, *args, **kwargs):
        self.medias.append(BililiMedia(*args, **kwargs, container=self))

    def __str__(self):
        return "{} 「{}」".format(self.name, quality_map[self.quality]["description"])


class BililiMedia:
    """ bilibili 媒体单元类
    从 B 站直接获取的可下载的媒体单元，可能是 flv、mp4、m4s
    """

    def __init__(self, id, url, quality, size, height, width, container, type="dash_video", block_size=0):

        self.id = id
        self.quality = quality
        self.height = height
        self.width = width
        self.url = url
        self.container = container
        self.block_size = block_size
        self.path = os.path.splitext(self.container.path)[0]
        if self.container.type == "flv":
            self.path += "_{:02d}.flv".format(id)
        elif self.container.type == "dash":
            self.path += "_{}.m4s".format(type)
        elif self.container.type == "mp4":
            self.path += "_dl.mp4"
        else:
            print("[warn] Unknown container type: {}".format(self.container.type))
        self.name = os.path.split(self.path)[-1]
        self._ = DownloaderMiddleware(parent=self.container._)
        self._.total_size = size

        if self.container.quality is None:
            self.container.quality = quality
        if self.container.width is None:
            self.container.width = width
        if self.container.height is None:
            self.container.height = height
        if self._.total_size == 0:
            print("[warn] {} 获取 size 为 0".format(self.name))
            self._.total_size = 0
        if self._.total_size is None:
            print("[warn] {} 无法获取 size".format(self.name))
            self._.total_size = 0

        self.blocks = self.chunking()

    def chunking(self):
        block_size = self.block_size
        blocks = []
        total_size = self._.total_size
        if block_size:
            block_range_list = [(i, i + block_size - 1) for i in range(0, total_size, block_size)]
            if total_size % block_size != 0:
                block_range_list[-1] = (total_size // block_size * block_size, total_size - 1)
        else:
            block_range_list = [(0, total_size - 1)]
        for i, block_range in enumerate(block_range_list):
            blocks.append(BililiBlock(id=i, url=self.url, media=self, block_size=block_size, range=block_range))
        assert self._.total_size == total_size, "重新设置的 total size 与原来值不匹配"
        return blocks


class BililiBlock:
    """ bilibili 媒体块类
    """

    def __init__(self, id, url, media, block_size, range):

        self.id = id
        self.url = url
        self.block_size = block_size
        self.media = media
        self.range = range
        # 假设最大 10 GB 时所需的位数
        ndigits = 1 if block_size == 0 else len(str(10 * 1024 * 1024 * 1024 // self.block_size))
        self.path = "_{:0{}}".format(self.id, ndigits).join(os.path.splitext(self.media.path))
        self.name = os.path.split(self.path)[-1]
        self._ = DownloaderMiddleware(parent=self.media._)
        self._.total_size = self.range[1] - self.range[0] + 1
