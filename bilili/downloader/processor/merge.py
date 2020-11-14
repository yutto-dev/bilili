import os

from bilili.downloader.processor.base import Processor
from bilili.utils.ffmpeg import FFmpeg


ffmpeg = FFmpeg()


class MergeProcessor(Processor):
    def merge(self, type, src_path_list=[], dst_path=""):
        if type == "mp4" or type is None:
            with open(dst_path, "wb") as fw:
                for src_path in src_path_list:
                    with open(src_path, "rb") as fr:
                        fw.write(fr.read())
        elif type == "flv":
            ffmpeg.join_videos(src_path_list, dst_path)
        elif type == "dash":
            if len(src_path_list) == 2:
                ffmpeg.join_video_audio(src_path_list[0], src_path_list[1], dst_path)
            else:
                ffmpeg.convert(src_path_list[0], dst_path)
        else:
            print("Unknown type {}".format(type))
        for src_path in src_path_list:
            os.remove(src_path)
