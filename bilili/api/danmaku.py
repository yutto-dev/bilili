import os

from bilili.tools import spider

danmaku_api = "http://comment.bilibili.com/{cid}.xml"

def get_danmaku(container):
    # 下载弹幕
    danmaku_url = danmaku_api.format(cid=container.meta['cid'])
    res = spider.get(danmaku_url)
    res.encoding = "utf-8"
    danmaku_path = os.path.splitext(container.path)[0] + ".xml"
    with open(danmaku_path, "w", encoding="utf-8") as f:
        f.write(res.text)
