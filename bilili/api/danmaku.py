import xml.etree.ElementTree as ET
from typing import Any

from ..api.exports import export_api
from ..tools import spider


@export_api(route="/danmaku/xml")
def get_danmaku(cid: str) -> str:
    danmaku_api = "http://comment.bilibili.com/{cid}.xml"
    res = spider.get(danmaku_api.format(cid=cid))
    res.encoding = "utf-8"
    return res.text


@export_api(route="/danmaku/dplayer")
def get_danmaku_for_dplayer(cid: str) -> Any:
    xml = get_danmaku(cid)
    root = ET.fromstring(xml)
    data = []
    for child in root:
        if child.tag != "d":
            continue
        attrs = child.attrib["p"].split(",")
        text = child.text
        # fmt: off
        data.append(
            [
                float(attrs[0]),
                {"5": 1, "4": 2}.get(attrs[1], 0),
                int(attrs[3]),
                attrs[6],
                text
            ]
        )
        # fmt: on
    return data
