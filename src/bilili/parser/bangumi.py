from ..api.bangumi import get_bangumi_list, get_bangumi_playurl, get_bangumi_subtitle, get_bangumi_title


def get_title(resource_id):
    return get_bangumi_title(season_id=resource_id.season_id, episode_id=resource_id.episode_id)


def get_list(resource_id, with_section: bool = False):
    video_list = get_bangumi_list(
        season_id=resource_id.season_id, episode_id=resource_id.episode_id, with_section=with_section
    )
    return [
        {
            "id": video["id"],
            "name": video["name"],
            "meta": {
                "avid": video["avid"],
                "bvid": video["bvid"],
                "cid": video["cid"],
                "episode_id": video["episode_id"]
            },
        }
        for video in video_list
    ]  # fmt: skip


def get_playurl(container, quality, audio_quality):
    play_list = get_bangumi_playurl(
        avid=container.meta["avid"],
        episode_id=container.meta["episode_id"],
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
    return get_bangumi_subtitle(
        avid=container.meta["avid"],
        bvid=container.meta["bvid"],
        cid=container.meta["cid"],
    )
