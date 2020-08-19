from bilili.tools import spider
from bilili.api.exports import export_api


@export_api(route="/danmaku")
def get_danmaku(cid: str) -> str:
    danmaku_api = "http://comment.bilibili.com/{cid}.xml"
    res = spider.get(danmaku_api.format(cid=cid))
    res.encoding = "utf-8"
    return res.text
