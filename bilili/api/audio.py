import re
import json

from bilili.tools import spider, regex_bangumi_ep
from bilili.api.exceptions import ArgumentsError, BiliAPIError
from bilili.api.exports import export_api


@export_api(route="/audio/url")
def get_audio_url(audio_id: str = "") -> str:
    if not audio_id:
        raise ArgumentsError("audio_id")
    audio_api = "https://www.bilibili.com/audio/music-service-c/web/url?sid={audio_id}&privilege=2&quality=2"
    # 后面两个参数暂时意味不明
    res = spider.get(audio_api.format(audio_id=audio_id))
    res_json = res.json()
    if res_json["code"] != 0:
        raise BiliAPIError(res_json["code"], res_json["msg"])
    res_data = res_json["data"]
    return res_data["cdns"][0]
