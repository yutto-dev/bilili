import os
import time

from utils.common import get_size, size_format


def download_segment(segment_info, video_info, GLOBAL):
    """ 下载视频片段，并检查该视频是否所有片段下载完成
    最后一个下载完成的片段对视频进行合并
    """
    spider = GLOBAL["spider"]
    ffmpeg = GLOBAL["ffmpeg"]

    print("-----> {} sp:{} {}/{}".format(
        video_info["name"], segment_info["sp"], segment_info["num"], len(video_info["segments"])).ljust(80))

    # 下载片段
    spider.download_bin(segment_info["url"], segment_info["file_path"])

    # 检查视频所有片段是否完成，若完成则合并
    segment_info["downloaded"] = True
    if all([segment["downloaded"] for segment in video_info["segments"]]):
        video_path_list = [segment["file_path"]
                           for segment in video_info["segments"]]
        ffmpeg.join_videos(video_path_list, video_info["file_path"])
        video_info["merged"] = True

        # 清除合并完成的视频片段
        for segment in video_info["segments"]:
            os.remove(segment["file_path"])


def manager(GLOBAL):
    """ 监控线程 """

    size, t = get_size(GLOBAL['base_dir']), time.time()
    while True:
        # 下载速度
        now_size, now_t = get_size(GLOBAL['video_dir']), time.time()
        delta_size, delta_t = now_size - size, now_t - t
        size, t = now_size, now_t
        if delta_t < 1e-6:
            delta_t = 1e-6
        speed = delta_size / delta_t

        # 下载进度
        num_done = 0
        total = len(GLOBAL["info"])
        length = 50
        for item in GLOBAL["info"]:
            if item["merged"]:
                num_done += 1
        len_done = 50 * num_done // total
        len_undone = 50 - len_done
        print('{}{} {:10}'.format(
            "#" * len_done, "_" * len_undone, size_format(speed)+"/s"), end='\r')

        # 监控是否全部完成
        if all([item["merged"] for item in GLOBAL["info"]]):
            print('\nEnjoy~')
            break

        time.sleep(0.1)
