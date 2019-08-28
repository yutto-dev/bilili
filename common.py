import os
import re
import time
import requests
import cv2

from utils.common import get_size, size_format, touch_dir,touch_file


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


def convert_danmaku(video_path_list):
    """ 将视频文件夹下的 xml 弹幕转换为 ass 弹幕 """
    # 检测插件是否已经就绪
    plugin_url = "https://raw.githubusercontent.com/m13253/danmaku2ass/master/danmaku2ass.py"
    plugin_path = "plugins/danmaku2ass.py"
    touch_dir(os.path.dirname(plugin_path))
    touch_file(os.path.join(os.path.dirname(plugin_path), "__init__.py"))
    if not os.path.exists(plugin_path):
        print("下载插件中……")
        res = requests.get(plugin_url)
        with open(plugin_path, "w", encoding="utf8") as f:
            f.write(res.text)

    # 使用插件进行转换
    from plugins.danmaku2ass import Danmaku2ASS
    for video_path in video_path_list:
        name = os.path.splitext(video_path)[0]
        print("convert {}".format(os.path.split(name)[-1]), end="\r")
        if not os.path.exists(name+".mp4") or \
            not os.path.exists(name+".xml"):
            continue
        cap = cv2.VideoCapture(name+".mp4")
        __, frame = cap.read()
        h, w, __ = frame.shape
        Danmaku2ASS(
            name+".xml", "autodetect", name+".ass",
            w, h, reserve_blank=0,
            font_face=_('(FONT) sans-serif')[7:],
            font_size=w/40, text_opacity=0.8, duration_marquee=15.0,
            duration_still=10.0, comment_filter=None, is_reduce_comments=False,
            progress_callback=None)


def download_segment(segment_info, video_info, spider, ffmpeg):
    """ 下载视频片段，并检查该视频是否所有片段下载完成
    最后一个下载完成的片段对视频进行合并
    """

    print("-----> {} sp:{} {}/{}".format(
        video_info["name"], segment_info["sp"], segment_info["id"], len(video_info["segments"])).ljust(80))

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


def manager(info, video_dir):
    """ 监控线程 """

    size, t = get_size(video_dir), time.time()
    while True:
        # TODO:
        # 当前仅使用本地文件简单地统计速度与进度，会与实际值有所偏差，待改进

        # 下载速度
        now_size, now_t = get_size(video_dir), time.time()
        delta_size, delta_t = now_size - size, now_t - t
        size, t = now_size, now_t
        if delta_t < 1e-6:
            delta_t = 1e-6
        speed = delta_size / delta_t

        # 下载进度
        num_done = 0
        total = len(info)
        length = 50
        for item in info:
            if item["merged"]:
                num_done += 1
        len_done = length * num_done // total
        len_undone = length - len_done
        print('{}{} {:12}'.format(
            "#" * len_done, "_" * len_undone, size_format(speed)+"/s").ljust(80), end='\r')

        # 监控是否全部完成
        if all([item["merged"] for item in info]):
            print("\n视频已全部下载完成!")
            break

        try:
            time.sleep(1)
        except (SystemExit, KeyboardInterrupt):
            raise
