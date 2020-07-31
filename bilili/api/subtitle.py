import json
import re
import os

from bilili.utils.subtitle import Subtitle
from bilili.tools import spider


subtitle_api = "https://api.bilibili.com/x/player.so?id=cid:{cid}&aid={avid}&bvid={bvid}"


def get_subtitle(container):
    cid, avid, bvid = container.meta["cid"], container.meta["avid"], container.meta["bvid"]
    # 检查是否有字幕并下载
    subtitle_url = subtitle_api.format(avid=avid, cid=cid, bvid=bvid)
    res = spider.get(subtitle_url)
    subtitles_info = json.loads(
        re.search(r"<subtitle>(.+)</subtitle>", res.text).group(1))
    for sub_info in subtitles_info["subtitles"]:
        sub_path = os.path.splitext(
            container.path)[0] + sub_info["lan_doc"] + ".srt"
        subtitle = Subtitle(sub_path)
        for sub_line in spider.get("https:"+sub_info["subtitle_url"]).json()["body"]:
            subtitle.write_line(
                sub_line["content"], sub_line["from"], sub_line["to"])
