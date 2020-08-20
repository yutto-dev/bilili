import os

from bilili.events.base import Handler
from bilili.utils.ffmpeg import FFmpeg


ffmpeg = FFmpeg()


class MergingFile(Handler):
    def __init__(self, type, src_path_list=[], dst_path=""):
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
            ffmpeg.join_video_audio(self.src_path_list[0], self.src_path_list[1], self.dst_path)
        else:
            print("Unknown type {}".format(self.type))
        for src_path in self.src_path_list:
            os.remove(src_path)
        self.merged(self)
