import os
from bilili.api.space import get_space_title,get_space_video
from bilili.api.acg_video import get_acg_video_list


def get_title(resource_id):
    return get_space_title(spaceid=resource_id.spaceid)


def get_list(resource_id):
    space_video_list = get_space_video(mid=resource_id.spaceid)
    video_list=[]
    for video in space_video_list:
        for list in get_acg_video_list(avid=video["avid"], bvid=video["bvid"],video_name =video["name"]):
            video_list.append(list)

    # print(video_list)

    return [
        {
            "id": video["id"],
            "name": video["name"] if video["name"] !="" else video["video_name"],
            "video_name": video["video_name"],
            # fmt: off
            "meta": {
                "avid": video["avid"],
                "bvid": video["bvid"],
                "cid": video["cid"]
            },
        }
        for video in video_list
    ]
