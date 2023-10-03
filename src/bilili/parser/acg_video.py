from ..api.acg_video import get_acg_video_list, get_acg_video_playurl, get_acg_video_subtitle, get_acg_video_title


def get_title(resource_id):
    return get_acg_video_title(avid=resource_id.avid, bvid=resource_id.bvid)


def get_list(resource_id, with_section: bool = False):
    video_list = get_acg_video_list(avid=resource_id.avid, bvid=resource_id.bvid)
    return [
        {
            "id": video["id"],
            "name": video["name"],
            "meta": {
                "avid": resource_id.avid,
                "bvid": resource_id.bvid,
                "cid": video["cid"]
            },
        }
        for video in video_list
    ]  # fmt: skip


def get_playurl(container, quality, audio_quality):
    play_list = get_acg_video_playurl(
        avid=container.meta["avid"],
        bvid=container.meta["bvid"],
        cid=container.meta["cid"],
        quality=quality,
        audio_quality=audio_quality,
        type=container.type,
    )
    return [
        {
            "id": play_info["id"],
            "url": play_info["url"],
            "mirrors": play_info["mirrors"],
            "quality": play_info["quality"],
            "height": play_info["height"],
            "width": play_info["width"],
            "size": play_info["size"],
            "type": play_info["type"],
        }
        for play_info in play_list
    ]


def get_subtitle(container):
    return get_acg_video_subtitle(
        avid=container.meta["avid"],
        bvid=container.meta["bvid"],
        cid=container.meta["cid"],
    )
