import re
import json

from bilili.tools import spider
from bilili.api.exports import export_api


@export_api(route="/subtitle")
def get_subtitle(avid: str = "", bvid: str = "", cid: str = ""):
    if not (avid or bvid):
        raise ArgumentsError("avid", "bvid")
    subtitle_api = "https://api.bilibili.com/x/player.so?id=cid:{cid}&aid={avid}&bvid={bvid}"
    subtitle_url = subtitle_api.format(avid=avid, cid=cid, bvid=bvid)
    res = spider.get(subtitle_url)
    subtitles_info = json.loads(re.search(r"<subtitle>(.+)</subtitle>", res.text).group(1))
    return [
        # fmt: off
        {
            "lang": sub_info["lan_doc"],
            "lines": spider.get("https:" + sub_info["subtitle_url"]).json()["body"]
        }
        for sub_info in subtitles_info["subtitles"]
    ]
