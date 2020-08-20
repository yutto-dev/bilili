from bilili.api.bangumi import get_bangumi_title, get_bangumi_list, get_bangumi_playurl


def get_title(resource_id):
    return get_bangumi_title(season_id=resource_id.season_id, episode_id=resource_id.episode_id)


def get_list(resource_id):
    video_list = get_bangumi_list(season_id=resource_id.season_id, episode_id=resource_id.episode_id)
    return [
        {
            "id": video["id"],
            "name": video["name"],
            # fmt: off
            "meta": {
                "avid": video["avid"],
                "bvid": video["bvid"],
                "cid": video["cid"],
                "episode_id": video["episode_id"]
            },
        }
        for video in video_list
    ]


def get_playurl(container, quality):
    play_list = get_bangumi_playurl(
        avid=container.meta["avid"],
        episode_id=container.meta["episode_id"],
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
