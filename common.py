import os
import re
import time

from utils.common import get_size, size_format


def parse_episodes(episodes_str, total):
    """ 将选集字符串转为列表 """

    # 解析字符串为列表
    print("全 {} 话".format(total))
    if episodes_str == "all":
        episode_list = list(range(1, total+1))
    elif re.match(r"\d+~\d+", episodes_str):
        start, end = episodes_str.split("~")
        start, end = int(start), int(end)
        assert end > start, "终点值应大于起点值"
        episode_list = list(range(start, end+1))
    elif re.match(r"\d+(,\d+)*", episodes_str):
        episode_list = episodes_str.split(",")
        episode_list = list(map(int, episode_list))
    else:
        episode_list = []

    # 筛选满足条件的剧集
    out_of_range = []
    episodes = []
    for episode in episode_list:
        if episode in range(1, total+1):
            if episode not in episodes:
                episodes.append(episode)
        else:
            out_of_range.append(episode)
    if out_of_range:
        print("warn: 剧集 {} 不存在".format(",".join(list(map(str, out_of_range)))))

    print("已选择第 {} 话".format(",".join(list(map(str, episodes)))))
    assert episodes, "没有选中任何剧集"
    return episodes


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
        # TODO:
        # 当前仅使用本地文件简单地统计速度与进度，会与实际值有所偏差，待改进

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
            "#" * len_done, "_" * len_undone, size_format(speed)+"/s").ljust(80), end='\r')

        # 监控是否全部完成
        if all([item["merged"] for item in GLOBAL["info"]]):
            print('\nEnjoy~')
            break

        time.sleep(0.1)
