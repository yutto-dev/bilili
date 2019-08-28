import os
import re
import threading

from common import parse_episodes
from utils.common import repair_filename, touch_dir
from utils.crawler import BililiCrawler
from utils.playlist import Dpl, M3u

info_api = "https://api.bilibili.com/pgc/web/season/section?season_id={season_id}"
parse_api = "https://api.bilibili.com/pgc/player/web/playurl?avid={avid}&cid={cid}&qn={sp}&ep_id={ep_id}"
danmaku_api = "http://comment.bilibili.com/{cid}.xml"
spider = BililiCrawler()
CONFIG = dict()
exports = dict()
__all__ = ["exports"]


def get_title(url):
    """ 获取视频标题 """
    res = spider.get(url)
    title = re.search(
        r'<span class="media-info-title-t">(.*?)</span>', res.text).group(1)
    return title


def get_info(url):
    """ 从 url 中获取视频所需信息 """
    info = []
    season_id = re.search(
        r'"param":{"season_id":(\d+),"season_type":\d+}', spider.get(url).text).group(1)

    info_url = info_api.format(season_id=season_id)
    res = spider.get(info_url)

    for i, item in enumerate(res.json()["result"]["main_section"]["episodes"]):
        index = item["title"]
        if re.match(r'^\d*\.?\d*$', index):
            index = '第{}话'.format(index)
        name = repair_filename(' '.join([index, item["long_title"]]))
        file_path = os.path.join(CONFIG['video_dir'], repair_filename(
            '{}.mp4'.format(name)))
        if CONFIG['playlist'] is not None:
            CONFIG['playlist'].write_path(file_path)
        info.append({
            "id": i+1,
            "aid": item["aid"],
            "cid": item["cid"],
            "epid": item["id"],
            "name": name,
            "file_path": file_path,
            "merged": False,
            "segments": []
        })

    return info


def parse_segment_info(item):
    """ 解析视频片段 url """

    segments = []
    aid, cid, ep_id = item["aid"], item["cid"], item["epid"]

    # 下载弹幕
    danmaku_url = danmaku_api.format(cid=cid)
    res = spider.get(danmaku_url)
    res.encoding = "utf-8"
    danmaku_path = os.path.splitext(item["file_path"])[0] + ".xml"
    with open(danmaku_path, "w", encoding="utf-8") as f:
        f.write(res.text)

    # 检查是否可以下载，同时搜索支持的清晰度，并匹配最佳清晰度
    touch_message = spider.get(parse_api.format(
        avid=aid, cid=cid, ep_id=ep_id, sp=80)).json()
    if touch_message["code"] != 0:
        print("warn: 无法下载 {} ，原因： {}".format(
            item["name"], touch_message["message"]))
        item["merged"] = True
        return
    if touch_message["result"]["is_preview"] == 1:
        print("warn: {} 为预览版视频".format(item["name"]))

    accept_quality = touch_message['result']['accept_quality']
    for sp in CONFIG['sp_seq']:
        if sp in accept_quality:
            break

    parse_url = parse_api.format(avid=aid, cid=cid, ep_id=ep_id, sp=sp)
    res = spider.get(parse_url)

    for i, segment in enumerate(res.json()['result']['durl']):
        id = i + 1
        file_path = os.path.join(CONFIG['video_dir'], repair_filename(
                                '{}_{:02d}.flv'.format(item["name"], id)))
        segments.append({
            "id": id,
            "url": segment["url"],
            "sp": sp,
            "file_path": file_path,
            "downloaded": False
        })
    item["segments"] = segments


def parse(url, config):
    # 获取标题
    CONFIG.update(config)
    title = get_title(url)
    print(title)

    # 创建所需目录结构
    CONFIG["base_dir"] = touch_dir(os.path.join(
        CONFIG['dir'], title + " - bilibili"))
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
    info = get_info(url)
    CONFIG["info"] = info
    if CONFIG['playlist'] is not None:
        CONFIG['playlist'].flush()

    # 解析并过滤需要的选集
    episodes = parse_episodes(CONFIG["episodes"], len(info))
    info = list(filter(lambda item: item["id"] in episodes, info))
    CONFIG["info"] = info

    # 解析片段信息及视频 url
    for i, item in enumerate(info):
        print("{:02}/{:02} parsing segments info...".format(i, len(info)), end="\r")
        parse_segment_info(item)

    # 导出下载所需数据
    exports.update({
        "info": info,
        "spider": spider,
        "video_dir": CONFIG["video_dir"]
    })
