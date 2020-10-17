import re

from typing import List


def parse_episodes(episodes_str: str, total: int) -> List[int]:
    """ 将选集字符串转为列表 """

    def reslove_negetive(value):
        return value if value > 0 else value + total + 1

    # 解析字符串为列表
    print("全 {} 话".format(total))
    if re.match(r"([\-\d\^\$]+(~[\-\d\^\$]+)?)(,[\-\d\^\$]+(~[\-\d\^\$]+)?)*", episodes_str):
        episodes_str = episodes_str.replace("^", "1")
        episodes_str = episodes_str.replace("$", "-1")
        episode_list = []
        for episode_item in episodes_str.split(","):
            if "~" in episode_item:
                start, end = episode_item.split("~")
                start, end = int(start), int(end)
                start, end = reslove_negetive(start), reslove_negetive(end)
                assert end >= start, "终点值（{}）应不小于起点值（{}）".format(end, start)
                episode_list.extend(list(range(start, end + 1)))
            else:
                episode_item = int(episode_item)
                episode_item = reslove_negetive(episode_item)
                episode_list.append(episode_item)
    else:
        episode_list = []

    episode_list = sorted(list(set(episode_list)))

    # 筛选满足条件的剧集
    out_of_range = []
    episodes = []
    for episode in episode_list:
        if episode in range(1, total + 1):
            if episode not in episodes:
                episodes.append(episode)
        else:
            out_of_range.append(episode)
    if out_of_range:
        print("warn: 剧集 {} 不存在".format(",".join(list(map(str, out_of_range)))))

    print("已选择第 {} 话".format(",".join(list(map(str, episodes)))))
    assert episodes, "没有选中任何剧集"
    return episodes
