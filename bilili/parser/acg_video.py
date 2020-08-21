import os
from bilili.api.acg_video import get_acg_video_title, get_acg_video_list, get_acg_video_playurl


def get_title(resource_id):
    return get_acg_video_title(avid=resource_id.avid, bvid=resource_id.bvid)


def get_list(resource_id):
    video_list = get_acg_video_list(avid=resource_id.avid, bvid=resource_id.bvid)
    return [
        {
            "id": video["id"],
            "name": video["name"],
            # fmt: off
            "meta": {
                "avid": resource_id.avid,
                "bvid": resource_id.bvid,
                "cid": video["cid"]
            },
        }
        for video in video_list
    ]


def get_playurl(container, quality):
    play_list = get_acg_video_playurl(
        avid=container.meta["avid"],
        bvid=container.meta["bvid"],
        cid=container.meta["cid"],
        quality=quality,
        type=container.type,
    )
    return [
        {
            "id": play_info["id"],
            "url": play_info["url"],
            "quality": play_info["quality"],
            "height": play_info["height"],
            "width": play_info["width"],
            "size": play_info["size"],
            "type": play_info["type"],
        }
        for play_info in play_list
    ]
