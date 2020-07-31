import re
import os

from bilili.tools import spider
from bilili.utils.quality import quality_map
from bilili.video import BililiContainer
from bilili.utils.base import repair_filename, touch_dir, touch_url

info_api = "https://api.bilibili.com/pgc/web/season/section?season_id={season_id}"
parse_api = "https://api.bilibili.com/pgc/player/web/playurl?avid={avid}&cid={cid}&qn={qn}&ep_id={ep_id}"


def get_title(home_url):
    """ 获取视频标题 """
    res = spider.get(home_url)
    title = re.search(
        r'<span class="media-info-title-t">(.*?)</span>', res.text).group(1)
    return title

def get_context(home_url):
    context = {
        'season_id': '',
    }

    season_id = re.search(
        r'"param":{"season_id":(\d+),"season_type":\d+}', spider.get(home_url).text).group(1)
    context['season_id'] = season_id

    return context

def get_containers(context, video_dir, format, playlist=None):
    season_id = context['season_id']
    containers = []
    info_url = info_api.format(season_id=season_id)
    res = spider.get(info_url)

    for i, item in enumerate(res.json()["result"]["main_section"]["episodes"]):
        index = item["title"]
        if re.match(r'^\d*\.?\d*$', index):
            index = '第{}话'.format(index)
        name = repair_filename(' '.join([index, item["long_title"]]))
        file_path = os.path.join(video_dir, repair_filename(
            '{}.mp4'.format(name)))
        if playlist is not None:
            playlist.write_path(file_path)
        containers.append(BililiContainer(
            id=i+1,
            name=name,
            path=file_path,
            meta={
                "aid": item["aid"],
                "cid": item["cid"],
                "epid": item["id"],
                "bvid": ''
            },
            format=format,
        ))
    if playlist is not None:
        playlist.flush()

    return containers

def parse_segments(container, quality_sequence):
    aid, cid, ep_id, bvid = container.meta["aid"], container.meta["cid"], container.meta["epid"], container.meta["bvid"]

    if container.format == "flv":
        # 检查是否可以下载，同时搜索支持的清晰度，并匹配最佳清晰度
        touch_message = spider.get(parse_api.format(
            avid=aid, cid=cid, ep_id=ep_id, qn=80)).json()
        if touch_message["code"] != 0:
            print("warn: 无法下载 {} ，原因： {}".format(
                container.name, touch_message["message"]))
            return
        if touch_message["result"]["is_preview"] == 1:
            print("warn: {} 为预览版视频".format(container.name))

        accept_quality = touch_message['result']['accept_quality']
        for qn in quality_sequence:
            if qn in accept_quality:
                break

        parse_url = parse_api.format(avid=aid, cid=cid, ep_id=ep_id, qn=qn)
        res = spider.get(parse_url)

        for i, segment in enumerate(res.json()['result']['durl']):
            container.append_media(
                id=i+1,
                url=segment["url"],
                qn=qn,
                height=quality_map[qn]['height'],
                width=quality_map[qn]['width'],
                size=segment["size"],
                type="segment",
            )
    elif container.format == "m4s":
        # 检查是否可以下载，同时搜索支持的清晰度，并匹配最佳清晰度
        parse_api_m4s = parse_api + "&fnver=0&fnval=16&fourk=1"
        play_info = spider.get(parse_api_m4s.format(
            avid=aid, cid=cid, ep_id=ep_id, qn=quality_sequence[0], bvid=bvid)).json()
        if play_info["code"] != 0:
            print("warn: 无法下载 {} ，原因： {}".format(
                container.name, play_info["message"]))
            return
        if play_info["result"]["is_preview"] == 1:
            print("warn: {} 为预览版视频".format(container.name))

        # accept_quality = play_info['result']['accept_quality']
        accept_quality = set([video['id']
                            for video in play_info['result']['dash']['video']])
        for qn in quality_sequence:
            if qn in accept_quality:
                break

        for video in play_info['result']['dash']['video']:
            if video['id'] == qn:
                container.append_media(
                    id=1,
                    url=video['base_url'],
                    qn=qn,
                    height=video['height'],
                    width=video['width'],
                    size=touch_url(video['base_url'], spider)[0],
                    type="video"
                )
                break
        for audio in play_info['result']['dash']['audio']:
            container.append_media(
                id=2,
                url=audio['base_url'],
                height=None,
                width=None,
                size=touch_url(audio['base_url'], spider)[0],
                qn=qn,
                type="audio"
            )
            break

    elif container.format == 'mp4':
        print("番剧不支持 mp4 format")
    else:
        print("Unknown format {}".format(container.format))
