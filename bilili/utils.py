import os
import re
import time
import requests
import cv2

from bilili.common.base import get_size, size_format, touch_dir, touch_file, Task
from bilili.common.thread import ThreadPool


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
        print("convert {} ".format(os.path.split(name)[-1]), end="\r")
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
