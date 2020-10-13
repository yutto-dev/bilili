import re,time

from bilili.tools import spider
from bilili.quality import gen_quality_sequence, video_quality_map, Media
from bilili.utils.base import touch_url

from bilili.api.exports import export_api


@export_api(route="/space/title")
def get_space_title(spaceid: str = "") -> str:
    if not (spaceid):
        raise Exception(spaceid +"不存在")
    home_url = (
        "https://space.bilibili.com/{spaceid}/".format(spaceid=spaceid)
    )
    res = spider.get(home_url)
    regex_title = re.compile(r"<title>(.*)的个人空间.*?</title>")
    if regex_title.search(res.text):
        title = regex_title.search(res.text).group(1)
    else:
        title = "呐，我也不知道是什么标题呢～"
    return title

@export_api(route="/space/title")
def get_space_video(mid: str = "" ,pn=1) -> str:
    if not (mid):
        raise Exception(mid +"不存在")
    list_api = "https://api.bilibili.com/x/space/arc/search?mid={mid}&pn={pn}&ps=100&jsonp=jsonp"
    album_list = []
    while True:
        res = spider.get(list_api.format(mid=mid, pn=pn))
        # 循环获取列表
        album_list.extend(
            [
                {
                    "id": i + 1,
                    "name": re.sub(r"[\/\\\:\*\?\"\<\>\|]", "", item["title"]),
                    "avid": str(item["aid"]),
                    "bvid": item["bvid"],
                }
                for i,item in enumerate(res.json()["data"]["list"]["vlist"])
            ]
        )
        if len(album_list) < int(res.json()['data']["page"]['count']):
            pn += 1
        else:
            break


    # 返回视频列表
    return album_list
