from ..tools import spider
from .utils import MaxRetry


@MaxRetry(2)
def get_danmaku(cid: str) -> str:
    danmaku_api = "http://comment.bilibili.com/{cid}.xml"
    res = spider.get(danmaku_api.format(cid=cid), timeout=(3, 18))
    res.encoding = "utf-8"
    return res.text
