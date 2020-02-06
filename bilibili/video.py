import os
import re
import threading
import json

from utils.common import parse_episodes
from utils.downloader import BililiVideo, BililiVideoSegment, Status
from common.base import repair_filename, touch_dir
from common.crawler import BililiCrawler
from common.playlist import Dpl, M3u
from common.subtitle import Subtitle


info_api = "https://api.bilibili.com/x/player/pagelist?aid={avid}&jsonp=jsonp"
parse_api = "https://api.bilibili.com/x/player/playurl?avid={avid}&cid={cid}&qn={qn}&type=&otype=json"
subtitle_api = "https://api.bilibili.com/x/player.so?id=cid:{cid}&aid={avid}"
danmaku_api = "http://comment.bilibili.com/{cid}.xml"
spider = BililiCrawler()
CONFIG = dict()
exports = dict()
__all__ = ["exports"]


def get_title(url):
    """ 获取视频标题 """
    res = spider.get(url)
    title = re.search(
        r'<title .*>(.*)_哔哩哔哩 \(゜-゜\)つロ 干杯~-bilibili</title>', res.text).group(1)
    return title


def get_videos(url):
    """ 从 url 中获取视频列表 """
    videos = []
    if re.match(r"https?://www.bilibili.com/video/av(\d+)", url):
        avid = re.match(r'https?://www.bilibili.com/video/av(\d+)', url).group(1)
    elif re.match(r"https?://b23.tv/av(\d+)", url):
        avid = re.match(r"https?://b23.tv/av(\d+)", url).group(1)
    CONFIG["avid"] = avid

    info_url = info_api.format(avid=avid)
    res = spider.get(info_url)

    for i, item in enumerate(res.json()["data"]):
        file_path = os.path.join(CONFIG['video_dir'], repair_filename(
            '{}.mp4'.format(item["part"])))
        if CONFIG['playlist'] is not None:
            CONFIG['playlist'].write_path(file_path)
        videos.append(BililiVideo(
            id = i+1,
            name = item["part"],
            path = file_path,
            meta = {
                "cid": item["cid"]
            },
            segmentation = CONFIG["segmentation"],
            block_size = CONFIG["block_size"],
            overwrite = CONFIG["overwrite"],
            spider = spider
        ))
    return videos


def parse_segment_info(video):
    """ 解析视频片段 url """

    cid, avid = video.meta["cid"], CONFIG["avid"]

    # 检查是否有字幕并下载
    subtitle_url = subtitle_api.format(avid=avid, cid=cid)
    res = spider.get(subtitle_url)
    subtitles_info = json.loads(re.search(r"<subtitle>(.+)</subtitle>", res.text).group(1))
    for sub_info in subtitles_info["subtitles"]:
        sub_path = os.path.splitext(video.path)[0] + sub_info["lan_doc"] + ".srt"
        subtitle = Subtitle(sub_path)
        for sub_line in spider.get("https:"+sub_info["subtitle_url"]).json()["body"]:
            subtitle.write_line(sub_line["content"], sub_line["from"], sub_line["to"])

    # 下载弹幕
    danmaku_url = danmaku_api.format(cid=cid)
    res = spider.get(danmaku_url)
    res.encoding = "utf-8"
    danmaku_path = os.path.splitext(video.path)[0] + ".xml"
    with open(danmaku_path, "w", encoding="utf-8") as f:
        f.write(res.text)

    # 检查是否可以下载，同时搜索支持的清晰度，并匹配最佳清晰度
    touch_message = spider.get(parse_api.format(
        avid=avid, cid=cid, qn=80)).json()
    if touch_message["code"] != 0:
        print("warn: 无法下载 {} ，原因： {}".format(
            video.name, touch_message["message"]))
        video.status.switch(Status.DONE)
        return

    accept_quality = touch_message['data']['accept_quality']
    for qn in CONFIG['qn_seq']:
        if qn in accept_quality:
            break

    parse_url = parse_api.format(avid=avid, cid=cid, qn=qn)
    res = spider.get(parse_url)

    for i, segment in enumerate(res.json()['data']['durl']):
        id = i + 1
        file_path = os.path.join(CONFIG['video_dir'], repair_filename(
                                '{}_{:02d}.flv'.format(video.name, id)))
        video.segments.append(BililiVideoSegment(
            id = id,
            path = file_path,
            url = segment["url"],
            size = segment["size"],
            qn = qn,
            video = video
        ))


def parse(url, config):
    # 获取标题
    CONFIG.update(config)
    spider.set_cookies(config["cookies"])
    title = get_title(url)
    print(title)

    # 创建所需目录结构
    CONFIG["base_dir"] = touch_dir(repair_filename(os.path.join(
        CONFIG['dir'], title + " - bilibili")))
    CONFIG["video_dir"] = touch_dir(os.path.join(CONFIG['base_dir'], "Videos"))
    if CONFIG["playlist_type"] == "dpl":
        CONFIG['playlist'] = Dpl(os.path.join(
            CONFIG['base_dir'], 'Playlist.dpl'), path_type=CONFIG["playlist_path_type"])
    elif CONFIG["playlist_type"] == "m3u":
        CONFIG['playlist'] = M3u(os.path.join(
            CONFIG['base_dir'], 'Playlist.m3u'), path_type=CONFIG["playlist_path_type"])
    else:
        CONFIG['playlist'] = None

    # 获取需要的信息
    videos = get_videos(url)
    CONFIG["videos"] = videos
    if CONFIG['playlist'] is not None:
        CONFIG['playlist'].flush()

    # 解析并过滤不需要的选集
    episodes = parse_episodes(CONFIG["episodes"], len(videos))
    videos = list(filter(lambda video: video.id in episodes, videos))
    CONFIG["videos"] = videos

    # 解析片段信息及视频 url
    for i, video in enumerate(videos):
        print("{:02}/{:02} parsing segments info...".format(i, len(videos)), end="\r")
        parse_segment_info(video)

    # 导出下载所需数据
    exports.update({
        "videos": videos,
        "video_dir": CONFIG["video_dir"]
    })
