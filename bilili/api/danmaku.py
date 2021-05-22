from ..tools import spider


def get_danmaku(cid: str) -> str:
    danmaku_api = "http://comment.bilibili.com/{cid}.xml"
    res = spider.get(danmaku_api.format(cid=cid))
    res.encoding = "utf-8"
    return res.text
