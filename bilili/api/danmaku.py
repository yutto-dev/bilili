from bilili.tools import spider
from bilili.api.exports import export_api

@export_api(route="/danmaku/xml")
def get_danmaku(cid: str) -> str:
    danmaku_api = "http://comment.bilibili.com/{cid}.xml"
    print(danmaku_api.format(cid=cid))
    try:
        res = spider.get(danmaku_api.format(cid=cid))
        res.encoding = "utf-8"
        response =res.text
    except:
        response =""
    return  response


@export_api(route="/danmaku/dplayer")
def get_danmaku_for_dplayer(cid: str) -> any:
    from bs4 import BeautifulSoup

    xml_text = get_danmaku(cid)
    soup = BeautifulSoup(xml_text, "lxml-xml")
    items = soup.find_all("d")
    data = []
    for item in items:
        attrs = item.attrs["p"].split(",")
        text = item.text
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
    return data
