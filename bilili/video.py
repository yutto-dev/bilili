import os

from .handlers.status import DownloaderStatus
from .quality import audio_quality_map, video_quality_map
from .tools import global_status
from .utils.base import repair_filename
from .utils.console.colorful import colored_string
from .utils.console.logger import Logger


class BililiContainer:
    """bilibili 媒体容器类
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
        self._ = DownloaderStatus(parent=global_status)

    def append_media(self, *args, **kwargs):
        self.medias.append(BililiMedia(*args, **kwargs, container=self))

    def __str__(self):
        quality_description: str = ""
        if self.type == "dash":
            quality_description = " & ".join(
                [
                    {
                        "dash_video": video_quality_map,
                        "dash_audio": audio_quality_map
                    }[media.type][media.quality]["description"]
                    for media in self.medias
                ]  # fmt: skip
            )
        else:
            assert self.quality is not None, "quality 仍然为 None"
            quality_description = video_quality_map[self.quality]["description"]
        return "{} 「{}」".format(
            colored_string(self.name, fore="magenta"), colored_string(quality_description, fore="cyan")
        )

    def check_needs_download(self, overwrite: bool = False):
        """检查是否需要下载"""
        if overwrite:
            if os.path.exists(self.path):
                os.remove(self.path)
            return True
        if os.path.exists(self.path):
            return False
        return True


class BililiMedia:
    """bilibili 媒体单元类
    从 B 站直接获取的可下载的媒体单元，可能是 flv、mp4、m4s
    """

    def __init__(
        self,
        id,
        url,
        quality,
        size,
        height,
        width,
        container,
        mirrors=[],
        type="dash_video",
        block_size=0,
    ):

        self.id = id
        self.quality = quality
        self.height = height
        self.width = width
        self.url = url
        self.mirrors = mirrors
        self.container = container
        self.block_size = block_size
        self.path = os.path.splitext(self.container.path)[0]
        self.type = type
        if self.container.type == "flv":
            self.path += "_{:02d}.flv".format(id)
        elif self.container.type == "dash":
            self.path += "_{}.m4s".format(type)
        elif self.container.type == "mp4":
            self.path += "_dl.mp4"
        else:
            Logger.warning("未知的容器类型：{}".format(self.container.type))
        self.name = os.path.split(self.path)[-1]
        self._ = DownloaderStatus(parent=self.container._)
        self._.total_size = size

        if self.container.quality is None:
            self.container.quality = quality
        if self.container.width is None:
            self.container.width = width
        if self.container.height is None:
            self.container.height = height
        if self._.total_size == 0:
            Logger.warning("{} 获取 size 为 0".format(self.name))
            self._.total_size = 0
        if self._.total_size is None:
            Logger.warning("{} 无法获取 size".format(self.name))
            self._.total_size = 0

        self.blocks = self.chunking()

    def chunking(self):
        block_size = self.block_size
        blocks = []
        total_size = self._.total_size
        if block_size:
            block_range_list = [(i, i + block_size - 1) for i in range(0, total_size, block_size)]
            if total_size % block_size != 0:
                block_range_list[-1] = (
                    total_size // block_size * block_size,
                    total_size - 1,
                )
        else:
            block_range_list = [(0, total_size - 1)]
        for i, block_range in enumerate(block_range_list):
            blocks.append(
                BililiBlock(
                    id=i,
                    url=self.url,
                    mirrors=self.mirrors,
                    media=self,
                    block_size=block_size,
                    range=block_range,
                )
            )
        assert self._.total_size == total_size, "重新设置的 total size 与原来值不匹配"
        return blocks

    def check_needs_download(self, overwrite=False):
        """检查是否需要下载"""
        if overwrite:
            if os.path.exists(self.path):
                os.remove(self.path)
            return True
        if os.path.exists(self.path):
            return False
        return True


class BililiBlock:
    """bilibili 媒体块类"""

    def __init__(self, id, url, mirrors, media, block_size, range):

        self.id = id
        self.url = url
        self.mirrors = mirrors
        self.block_size = block_size
        self.media = media
        self.range = range
        # 假设最大 10 GB 时所需的位数
        ndigits = 1 if block_size == 0 else len(str(10 * 1024 * 1024 * 1024 // self.block_size))
        self.path = "_{:0{}}".format(self.id, ndigits).join(os.path.splitext(self.media.path))
        self.name = os.path.split(self.path)[-1]
        self._ = DownloaderStatus(parent=self.media._)
        self._.total_size = self.range[1] - self.range[0] + 1

    def check_needs_download(self, overwrite=False):
        """检查是否需要下载"""
        if overwrite:
            if os.path.exists(self.path):
                os.remove(self.path)
            if os.path.exists(self.path + ".dl"):
                os.remove(self.path + ".dl")
            return True
        if os.path.exists(self.path):
            return False
        return True
