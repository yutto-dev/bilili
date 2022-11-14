import re

from ..api.exceptions import ArgumentsError, CannotDownloadError, IsPreviewError, UnknownTypeError, UnsupportTypeError
from ..quality import Media, gen_quality_sequence, video_quality_map
from ..tools import spider
from ..utils.base import touch_url
from .utils import MaxRetry


@MaxRetry(2)
def get_season_id(media_id: str) -> str:
    home_url = "https://api.bilibili.com/pgc/review/user?media_id={media_id}".format(media_id=media_id)
    res_json = spider.get(home_url).json()
    return str(res_json["result"]["media"]["season_id"])


@MaxRetry(2)
def get_bangumi_title(media_id: str = "", season_id: str = "", episode_id: str = "") -> str:
    if not (media_id or season_id or episode_id):
        raise ArgumentsError("media_id", "season_id", "episode_id")
    title = "呐，我也不知道是什么标题呢～"
    if media_id:
        home_url = "https://www.bilibili.com/bangumi/media/md{media_id}".format(media_id=media_id)
        res = spider.get(home_url, timeout=3)
        regex_title = re.compile(r'<span class="media-info-title-t">(.*?)</span>')
        if match_obj := regex_title.search(res.text):
            title = match_obj.group(1)
    elif season_id or episode_id:
        if season_id:
            play_url = "https://www.bilibili.com/bangumi/play/ss{season_id}".format(season_id=season_id)
        else:
            play_url = "https://www.bilibili.com/bangumi/play/ep{episode_id}".format(episode_id=episode_id)
        res = spider.get(play_url, timeout=3)
        regex_title = re.compile(r'<a href=".+" target="_blank" title="(.*?)" class="media-title">(?P<title>.*?)</a>')
        if match_obj := regex_title.search(res.text):
            title = match_obj.group("title")
    return title


@MaxRetry(2)
def get_bangumi_list(episode_id: str = "", season_id: str = "", with_section: bool = False):
    if not (season_id or episode_id):
        raise ArgumentsError("season_id", "episode_id")
    list_api = "http://api.bilibili.com/pgc/view/web/season?season_id={season_id}&ep_id={episode_id}"
    res = spider.get(list_api.format(episode_id=episode_id, season_id=season_id), timeout=3)
    result = res.json()["result"]
    section_episodes = []

    if with_section and result.get("section", []):
        for section in result["section"]:
            section_episodes += section["episodes"]

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
        for i, item in enumerate(result["episodes"] + section_episodes)
    ]


@MaxRetry(2)
def get_bangumi_playurl(
    avid: str = "",
    bvid: str = "",
    episode_id: str = "",
    cid: str = "",
    quality: int = 127,
    audio_quality: int = 30280,
    type: str = "dash",
):
    video_quality_sequence = gen_quality_sequence(quality, type=Media.VIDEO)
    audio_quality_sequence = gen_quality_sequence(audio_quality, type=Media.AUDIO)
    play_api = "https://api.bilibili.com/pgc/player/web/playurl?avid={avid}&bvid={bvid}&ep_id={episode_id}&cid={cid}&qn={quality}"
    if type == "flv":
        touch_message = spider.get(
            play_api.format(avid=avid, bvid=bvid, episode_id=episode_id, cid=cid, quality=80), timeout=3
        ).json()
        if touch_message["code"] != 0:
            raise CannotDownloadError(touch_message["code"], touch_message["message"])
        if touch_message["result"]["is_preview"] == 1:
            raise IsPreviewError()

        accept_quality = touch_message["result"]["accept_quality"]
        for quality in video_quality_sequence:
            if quality in accept_quality:
                break

        play_url = play_api.format(avid=avid, bvid=bvid, episode_id=episode_id, cid=cid, quality=quality)
        res = spider.get(play_url, timeout=3)

        return [
            {
                "id": i + 1,
                "url": segment["url"],
                "mirrors": segment["backup_url"],
                "quality": quality,
                "height": video_quality_map[quality]["height"],
                "width": video_quality_map[quality]["width"],
                "size": segment["size"],
                "type": "flv_segment",
            }
            for i, segment in enumerate(res.json()["result"]["durl"])
        ]
    elif type == "dash":
        result = []
        play_api_dash = play_api + "&fnver=0&fnval=2000&fourk=1"
        play_info = spider.get(
            play_api_dash.format(
                avid=avid,
                bvid=bvid,
                episode_id=episode_id,
                cid=cid,
                quality=video_quality_sequence[0],
            ),
            timeout=3,
        ).json()

        if play_info["code"] != 0:
            raise CannotDownloadError(play_info["code"], play_info["message"])
        if play_info["result"].get("dash") is None:
            raise UnsupportTypeError("dash")
        if play_info["result"]["is_preview"] == 1:
            raise IsPreviewError()

        accept_video_quality = set([video["id"] for video in play_info["result"]["dash"]["video"]])
        for video_quality in video_quality_sequence:
            if video_quality in accept_video_quality:
                break
        else:
            video_quality = 127

        accept_audio_quality = set([audio["id"] for audio in play_info["result"]["dash"]["audio"]])
        for audio_quality in audio_quality_sequence:
            if audio_quality in accept_audio_quality:
                break
        else:
            audio_quality = 30280

        if play_info["result"]["dash"]["video"]:
            videos = play_info["result"]["dash"]["video"]
            for video in videos:
                if video["id"] == video_quality:
                    result.append(
                        {
                            "id": 1,
                            "url": video["base_url"],
                            "mirrors": video["backup_url"],
                            "quality": video_quality,
                            "height": video["height"],
                            "width": video["width"],
                            "size": touch_url(video["base_url"], spider)[0],
                            "type": "dash_video",
                        }
                    )
                    break
        if play_info["result"]["dash"]["audio"]:
            audios = play_info["result"]["dash"]["audio"]
            for audio in audios:
                if audio["id"] == audio_quality:
                    result.append(
                        {
                            "id": 2,
                            "url": audio["base_url"],
                            "mirrors": audio["backup_url"],
                            "quality": audio_quality,
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
        raise UnknownTypeError(type)


@MaxRetry(2)
def get_bangumi_subtitle(avid: str = "", bvid: str = "", cid: str = ""):
    if not (avid or bvid):
        raise ArgumentsError("avid", "bvid")
    subtitle_api = "https://api.bilibili.com/x/player/v2?cid={cid}&aid={avid}&bvid={bvid}"
    subtitle_url = subtitle_api.format(avid=avid, bvid=bvid, cid=cid)
    subtitles_info = spider.get(subtitle_url, timeout=3).json()["data"]["subtitle"]
    return [
        {
            "lang": sub_info["lan_doc"],
            "lines": spider.get("https:" + sub_info["subtitle_url"], timeout=(3, 10)).json()["body"]
        }
        for sub_info in subtitles_info["subtitles"]
    ]  # fmt: skip
