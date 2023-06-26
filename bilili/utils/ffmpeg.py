import os
import random
import shutil
import subprocess
from typing import List


class FFmpegNotFoundError(Exception):
    def __init__(self):
        super().__init__("请配置正确的 FFmpeg 路径")


class FFmpeg:
    """
    @refs : https://github.com/soimort/you-get
    """

    def __init__(self, ffmpeg_path: str = "ffmpeg", tmp_dir: str = ".ffmpeg_tmp"):
        try:
            if subprocess.run([ffmpeg_path], capture_output=True).returncode != 1:
                raise FFmpegNotFoundError()
        except FileNotFoundError:
            raise FFmpegNotFoundError()
        self.path = os.path.normpath(ffmpeg_path)
        tmp_dir = os.path.join(os.path.dirname(ffmpeg_path), tmp_dir)
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        self.tmp_dir = os.path.normpath(tmp_dir)

    def __del__(self):
        if hasattr(self, "tmp_dir") and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def exec(self, params: List[str]):
        """调用 ffmpeg"""
        cmd = [self.path]
        cmd.extend(params)
        return subprocess.run(cmd, capture_output=True)

    def convert(self, input_path: str, output_path: str) -> None:
        """视频格式转换"""
        params = [
            "-i", input_path,
            "-c", "copy",
            "-map", "0",
            "-y",
            output_path
        ]  # fmt: skip
        self.exec(params)

    def join_videos(self, video_path_list: List[str], output_path: str) -> None:
        """将视频拼接起来"""

        concat_list_path = os.path.join(self.tmp_dir, f"concat_list_{random.randint(0, 9999):04}.tmp").replace(
            "\\", "/"
        )
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for video_path in video_path_list:
                if os.path.isfile(video_path):
                    video_relpath = os.path.relpath(video_path, start=self.tmp_dir)
                    f.write(f"file '{video_relpath}'\n")
        params = [
            "-f", "concat",
            "-safe", "-1",
            "-i", concat_list_path,
            "-c", "copy",
            "-y",
            output_path
        ]  # fmt: skip
        self.exec(params)
        os.remove(concat_list_path)

    def join_video_audio(self, video_path: str, audio_path: str, output_path: str) -> None:
        """将视频和音频合并"""
        params = [
            "-i", video_path,
            "-i", audio_path,
            "-codec", "copy",
            "-y",
            output_path
        ]  # fmt: skip

        self.exec(params)
