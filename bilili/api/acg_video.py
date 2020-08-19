import re
import json

from bilili.tools import spider, regex_bangumi_ep
from bilili.quality import gen_quality_sequence, quality_map
from bilili.utils.base import touch_url
from bilili.api.exceptions import (
    ArgumentsError,
    CannotDownloadError,
    UnknownTypeError,
    UnsupportTypeError,
    IsPreviewError,
)
from bilili.api.exports import export_api


@export_api(route="/video_info")
def get_video_info(avid: str = "", bvid: str = ""):
    if not (avid or bvid):
        raise ArgumentsError("avid", "bvid")
    info_api = "http://api.bilibili.com/x/web-interface/view?aid={avid}&bvid={bvid}"
    res = spider.get(info_api.format(avid=avid, bvid=bvid))
    res_json_data = res.json()["data"]
    return {
        "avid": str(res_json_data["aid"]),
        "bvid": res_json_data["bvid"],
        "picture": res_json_data["pic"],
        "episode_id": regex_bangumi_ep.match(res_json_data["redirect_url"]).group("episode_id")
        if res_json_data.get("redirect_url")
        else "",
    }


@export_api(route="/acg_video/title")
def get_acg_video_title(avid: str = "", bvid: str = "") -> str:
    if not (avid or bvid):
        raise ArgumentsError("avid", "bvid")
    home_url = (
        "https://www.bilibili.com/video/{bvid}".format(bvid=bvid)
        if bvid
        else "https://www.bilibili.com/video/av{avid}".format(avid=avid)
    )
    res = spider.get(home_url)
    title = re.search(r"<title .*>(.*)_哔哩哔哩 \(゜-゜\)つロ 干杯~-bilibili</title>", res.text).group(1)
    return title


@export_api(route="/acg_video/list")
def get_acg_video_list(avid: str = "", bvid: str = ""):
    if not (avid or bvid):
        raise ArgumentsError("avid", "bvid")
    list_api = "https://api.bilibili.com/x/player/pagelist?aid={avid}&bvid={bvid}&jsonp=jsonp"
    res = spider.get(list_api.format(avid=avid, bvid=bvid))
    return [
        # fmt: off
        {
            'id': i + 1,
            'name': item['part'],
            'cid': str(item['cid'])
        }
        for i, item in enumerate(res.json()['data'])
    ]


@export_api(route="/acg_video/playurl")
def get_acg_video_playurl(avid: str = "", bvid: str = "", cid: str = "", quality: int = 120, type: str = "dash"):
    if not (avid or bvid):
        raise ArgumentsError("avid", "bvid")
    quality_sequence = gen_quality_sequence(quality)
    play_api = (
        "https://api.bilibili.com/x/player/playurl?avid={avid}&bvid={bvid}&cid={cid}&qn={quality}&type=&otype=json"
    )
    if type == "flv":
        touch_message = spider.get(play_api.format(avid=avid, bvid=bvid, cid=cid, quality=80)).json()
        if touch_message["code"] != 0:
            raise CannotDownloadError(touch_message["code"], touch_message["message"])

        accept_quality = touch_message["data"]["accept_quality"]
        for quality in quality_sequence:
            if quality in accept_quality:
                break

        play_url = play_api.format(avid=avid, bvid=bvid, cid=cid, quality=quality)
        res = spider.get(play_url)

        return [
            {
                "id": i + 1,
                "url": segment["url"],
                "quality": quality,
                "height": quality_map[quality]["height"],
                "width": quality_map[quality]["width"],
                "size": segment["size"],
                "type": "flv_segment",
            }
            for i, segment in enumerate(res.json()["data"]["durl"])
        ]
    elif type == "dash":
        result = []
        play_api_dash = play_api + "&fnver=0&fnval=16&fourk=1"
        touch_message = spider.get(
            play_api_dash.format(avid=avid, bvid=bvid, cid=cid, quality=quality_sequence[0])
        ).json()
        if touch_message["code"] != 0:
            raise CannotDownloadError(touch_message["code"], touch_message["message"])

        if touch_message["data"].get("dash") is None:
            raise UnsupportTypeError("dash")

        accept_quality = set([video["id"] for video in touch_message["data"]["dash"]["video"]])
        for quality in quality_sequence:
            if quality in accept_quality:
                break

        res = spider.get(play_api_dash.format(avid=avid, bvid=bvid, cid=cid, quality=quality))

        for video in res.json()["data"]["dash"]["video"]:
            if video["id"] == quality:
                result.append(
                    {
                        "id": 1,
                        "url": video["base_url"],
                        "quality": quality,
                        "height": video["height"],
                        "width": video["width"],
                        "size": touch_url(video["base_url"], spider)[0],
                        "type": "dash_video",
                    }
                )
                break
        for audio in res.json()["data"]["dash"]["audio"]:
            result.append(
                {
                    "id": 2,
                    "url": audio["base_url"],
                    "quality": quality,
                    "height": None,
                    "width": None,
                    "size": touch_url(audio["base_url"], spider)[0],
                    "type": "dash_audio",
                }
            )
            break
        return result
    elif type == "mp4":
        play_api_mp4 = play_api + "&platform=html5&high_quality=1"
        play_info = spider.get(play_api_mp4.format(avid=avid, bvid=bvid, cid=cid, quality=120)).json()
        if play_info["code"] != 0:
            raise CannotDownloadError(play_info["code"], play_info["message"])
        return [
            {
                "id": 1,
                "url": play_info["data"]["durl"][0]["url"],
                "quality": play_info["data"]["quality"],
                "height": quality_map[play_info["data"]["quality"]]["height"],
                "width": quality_map[play_info["data"]["quality"]]["width"],
                "size": play_info["data"]["durl"][0]["size"],
                "type": "mp4_container",
            }
        ]
    else:
        raise UnknownTypeError(type)
