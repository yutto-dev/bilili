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


@export_api(route="/get_season_id")
def get_season_id(media_id: str) -> str:
    home_url = "https://www.bilibili.com/bangumi/media/md{media_id}".format(media_id=media_id)
    season_id = re.search(r'"param":{"season_id":(\d+),"season_type":\d+}', spider.get(home_url).text).group(1)
    return str(season_id)


@export_api(route="/bangumi/title")
def get_bangumi_title(media_id: str = "", season_id: str = "", episode_id: str = "") -> str:
    if not (media_id or season_id or episode_id):
        raise ArgumentsError("media_id", "season_id", "episode_id")
    if media_id:
        home_url = "https://www.bilibili.com/bangumi/media/md{media_id}".format(media_id=media_id)
        res = spider.get(home_url)
        title = re.search(r'<span class="media-info-title-t">(.*?)</span>', res.text).group(1)
    elif season_id or episode_id:
        if season_id:
            play_url = "https://www.bilibili.com/bangumi/play/ss{season_id}".format(season_id=season_id)
        else:
            play_url = "https://www.bilibili.com/bangumi/play/ep{episode_id}".format(episode_id=episode_id)
        res = spider.get(play_url)
        title = re.search(
            r'<a href=".+" target="_blank" title="(.*?)" class="media-title">(?P<title>.*?)</a>', res.text
        ).group("title")
    return title


@export_api(route="/bangumi/list")
def get_bangumi_list(episode_id: str = "", season_id: str = ""):
    if not (season_id or episode_id):
        raise ArgumentsError("season_id", "episode_id")
    list_api = "http://api.bilibili.com/pgc/view/web/season?season_id={season_id}&ep_id={episode_id}"
    res = spider.get(list_api.format(episode_id=episode_id, season_id=season_id))
    return [
        {
            "id": i + 1,
            "name": " ".join(
                [
                    "第{}话".format(item["title"]) if re.match(r"^\d*\.?\d*$", item["title"]) else item["title"],
                    item["long_title"],
                ]
            ),
            "cid": str(item["cid"]),
            "episode_id": str(item["id"]),
            "avid": str(item["aid"]),
            "bvid": item["bvid"],
        }
        for i, item in enumerate(res.json()["result"]["episodes"])
    ]


@export_api(route="/bangumi/playurl")
def get_bangumi_playurl(
    avid: str = "", bvid: str = "", episode_id: str = "", cid: str = "", quality: int = 120, type: str = "dash"
):
    quality_sequence = gen_quality_sequence(quality)
    play_api = "https://api.bilibili.com/pgc/player/web/playurl?avid={avid}&bvid={bvid}&ep_id={episode_id}&cid={cid}&qn={quality}"
    if type == "flv":
        touch_message = spider.get(
            play_api.format(avid=avid, bvid=bvid, episode_id=episode_id, cid=cid, quality=80)
        ).json()
        if touch_message["code"] != 0:
            raise CannotDownloadError(touch_message["code"], touch_message["message"])
        if touch_message["result"]["is_preview"] == 1:
            raise IsPreviewError()

        accept_quality = touch_message["result"]["accept_quality"]
        for quality in quality_sequence:
            if quality in accept_quality:
                break

        play_url = play_api.format(avid=avid, bvid=bvid, episode_id=episode_id, cid=cid, quality=quality)
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
            for i, segment in enumerate(res.json()["result"]["durl"])
        ]
    elif type == "dash":
        result = []
        play_api_dash = play_api + "&fnver=0&fnval=16&fourk=1"
        play_info = spider.get(
            play_api_dash.format(avid=avid, bvid=bvid, episode_id=episode_id, cid=cid, quality=quality_sequence[0])
        ).json()
        if play_info["code"] != 0:
            raise CannotDownloadError(play_info["code"], play_info["message"])
        if play_info["result"].get("dash") is None:
            raise UnsupportTypeError("dash")
        if play_info["code"] != 0:
            raise CannotDownloadError(play_info["code"], play_info["message"])
        if play_info["result"]["is_preview"] == 1:
            raise IsPreviewError()

        accept_quality = set([video["id"] for video in play_info["result"]["dash"]["video"]])
        for quality in quality_sequence:
            if quality in accept_quality:
                break

        for video in play_info["result"]["dash"]["video"]:
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
        for audio in play_info["result"]["dash"]["audio"]:
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
        raise UnsupportTypeError("mp4")
    else:
        raise UnknownTypeError()
