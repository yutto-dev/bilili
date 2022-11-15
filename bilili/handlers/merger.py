import os
from typing import Callable, List

from ..handlers.base import Handler
from ..utils.console.logger import Logger
from ..utils.ffmpeg import FFmpeg

ffmpeg = FFmpeg(tmp_dir=".bilili_cache")


class MergingFile(Handler):
    before_merge: Callable[..., None]
    merged: Callable[..., None]

    def __init__(self, type: str, src_path_list: List[str] = [], dst_path: str = ""):
        super().__init__(["before_merge", "merged"])
        self.type = type
        self.src_path_list = src_path_list
        self.dst_path = dst_path

    def merge(self):
        self.before_merge(self)
        if self.type == "mp4" or self.type is None:
            with open(self.dst_path, "wb") as fw:
                for src_path in self.src_path_list:
                    with open(src_path, "rb") as fr:
                        fw.write(fr.read())
        elif self.type == "flv":
            ffmpeg.join_videos(self.src_path_list, self.dst_path)
        elif self.type == "dash":
            if len(self.src_path_list) == 2:
                ffmpeg.join_video_audio(self.src_path_list[0], self.src_path_list[1], self.dst_path)
            else:
                ffmpeg.convert(self.src_path_list[0], self.dst_path)
        else:
            Logger.error("未知类型： {}".format(self.type))
        for src_path in self.src_path_list:
            os.remove(src_path)
        self.merged(self)
