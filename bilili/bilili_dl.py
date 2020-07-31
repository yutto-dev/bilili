import re
import sys
import argparse
import os
import json
import cv2

from bilili.utils.base import repair_filename, touch_dir, touch_file, remove
from bilili.utils.playlist import Dpl, M3u
from bilili.api.subtitle import get_subtitle
from bilili.api.danmaku import get_danmaku
from bilili.tools import (aria2, ffmpeg, spider, regex_acg_video_av, regex_acg_video_av_short,
                          regex_acg_video_bv, regex_acg_video_bv_short, regex_bangumi)


def parse_episodes(episodes_str, total):
    """ 将选集字符串转为列表 """

    # 解析字符串为列表
    print("全 {} 话".format(total))
    if episodes_str == "all":
        episode_list = list(range(1, total+1))
    elif re.match(r"\d+~\d+", episodes_str):
        start, end = episodes_str.split("~")
        start, end = int(start), int(end)
        assert end > start, "终点值应大于起点值"
        episode_list = list(range(start, end+1))
    elif re.match(r"\d+(,\d+)*", episodes_str):
        episode_list = episodes_str.split(",")
        episode_list = list(map(int, episode_list))
    else:
        episode_list = []

    # 筛选满足条件的剧集
    out_of_range = []
    episodes = []
    for episode in episode_list:
        if episode in range(1, total+1):
            if episode not in episodes:
                episodes.append(episode)
        else:
            out_of_range.append(episode)
    if out_of_range:
        print("warn: 剧集 {} 不存在".format(",".join(list(map(str, out_of_range)))))

    print("已选择第 {} 话".format(",".join(list(map(str, episodes)))))
    assert episodes, "没有选中任何剧集"
    return episodes


def convert_danmaku(video_path_list):
    """ 将视频文件夹下的 xml 弹幕转换为 ass 弹幕 """
    # 检测插件是否已经就绪
    plugin_url = "https://raw.githubusercontent.com/m13253/danmaku2ass/master/danmaku2ass.py"
    plugin_path = "plugins/danmaku2ass.py"
    touch_dir(os.path.dirname(plugin_path))
    touch_file(os.path.join(os.path.dirname(plugin_path), "__init__.py"))
    if not os.path.exists(plugin_path):
        print("下载插件中……")
        res = requests.get(plugin_url)
        with open(plugin_path, "w", encoding="utf8") as f:
            f.write(res.text)

    # 使用插件进行转换
    from plugins.danmaku2ass import Danmaku2ASS
    for video_path in video_path_list:
        name = os.path.splitext(video_path)[0]
        print("convert {} ".format(os.path.split(name)[-1]), end="\r")
        if not os.path.exists(name+".mp4") or \
                not os.path.exists(name+".xml"):
            continue
        cap = cv2.VideoCapture(name+".mp4")
        __, frame = cap.read()
        h, w, __ = frame.shape
        Danmaku2ASS(
            name+".xml", "autodetect", name+".ass",
            w, h, reserve_blank=0,
            font_face=_('(FONT) sans-serif')[7:],
            font_size=w/40, text_opacity=0.8, duration_marquee=15.0,
            duration_still=10.0, comment_filter=None, is_reduce_comments=False,
            progress_callback=None)
        os.remove(name + '.xml')


def main():
    """ 解析命令行参数并调用相关模块进行下载 """

    parser = argparse.ArgumentParser(description="bilili B 站视频、弹幕下载器")
    parser.add_argument("url", help="视频主页地址")
    parser.add_argument('-f', '--format', default='m4s',
                        choices=['flv', 'm4s', 'mp4'], help="选择下载源格式（m4s 或 flv 或 mp4）")
    parser.add_argument("-d", "--dir", default=r"", help="下载目录")
    parser.add_argument("-q", "--quality", default='120', choices=['120', '116', '112', '80', '74', '64', '32', '16', '6'],
                        help="视频清晰度 120:4K, 116:1080P60, 112:1080P+, 80:1080P, 74:720P60, 64:720P, 32:480P, 16:360P, 6:240P")
    parser.add_argument("-p", "--episodes", default="all", help="选集")
    parser.add_argument("-w", "--overwrite",
                        action="store_true", help="强制覆盖已下载视频")
    parser.add_argument("-c", "--sess-data", default=None, help="输入 cookies")
    parser.add_argument("--ass", action="store_true",
                        help="自动将 xml 弹幕转换为 ass 弹幕")
    parser.add_argument("--playlist-type", default="dpl",
                        choices=["dpl", "m3u", "no"], help="播放列表类型，支持 dpl 和 m3u，输入 no 不生成播放列表")
    parser.add_argument("--path-type", default="rp",
                        help="播放列表路径类型（rp：相对路径，ap：绝对路径）")
    parser.add_argument("--danmaku", default="xml",
                        choices=["xml", "ass", "no"], help="弹幕类型，支持 xml 和 ass，如果设置为 no 则不下载弹幕")

    args = parser.parse_args()
    # 超清 4K 高清 1080P60 高清 1080P+ 高清 1080P  高清 720P60 高清 720P  清晰 480P  流畅 360P 极速 240P
    quality_lists = [120, 116, 112, 80, 74, 64, 32, 16, 6]
    cookies = {
        "SESSDATA": args.sess_data
    }

    config = {
        "url": args.url,
        "dir": args.dir,
        "quality_sequence": quality_lists[quality_lists.index(int(args.quality)):] +
        list(reversed(quality_lists[:quality_lists.index(int(args.quality))])),
        "episodes": args.episodes,
        "playlist_type": args.playlist_type,
        "playlist_path_type": args.path_type.upper(),
        "overwrite": args.overwrite,
        "cookies": cookies,
        "format": args.format.lower(),
    }

    if regex_acg_video_av.match(args.url) or \
       regex_acg_video_av_short.match(args.url) or \
       regex_acg_video_bv.match(args.url) or \
       regex_acg_video_bv_short.match(args.url):
        bili_type = "acg_video"
        from bilili.api.acg_video import get_title, get_context, get_containers, parse_segments
    elif regex_bangumi.match(args.url):
        bili_type = "bangumi"
        from bilili.api.bangumi import get_title, get_context, get_containers, parse_segments
    else:
        print("视频地址有误！")
        sys.exit(1)

    home_url = args.url

    # 获取标题
    spider.set_cookies(config["cookies"])
    title = get_title(home_url)
    print(title)

    # 创建所需目录结构
    base_dir = touch_dir(os.path.join(
        config['dir'], repair_filename(title + " - bilibili")))
    video_dir = touch_dir(os.path.join(base_dir, "Videos"))
    if args.overwrite:
        remove(video_dir)
        touch_dir(video_dir)
    if config['playlist_type'] == 'dpl':
        playlist = Dpl(os.path.join(base_dir, 'Playlist.dpl'),
                       path_type=config["playlist_path_type"])
    elif config["playlist_type"] == "m3u":
        playlist = M3u(os.path.join(base_dir, 'Playlist.m3u'),
                       path_type=config["playlist_path_type"])
    else:
        playlist = None

    # 获取需要的信息
    context = get_context(home_url)
    containers = get_containers(context, video_dir, config['format'], playlist)

    # 解析并过滤不需要的选集
    episodes = parse_episodes(config["episodes"], len(containers))
    containers = list(filter(lambda video: video.id in episodes, containers))

    # 解析片段信息及视频 url
    for i, container in enumerate(containers):
        print("{:02}/{:02} parsing segments info...".format(i,
                                                            len(containers)), end="\r")
        if bili_type == 'acg_video':
            get_subtitle(container)
        if args.danmaku != 'no':
            get_danmaku(container)
        parse_segments(container, config['quality_sequence'])

    if containers:
        containers_need_download = []
        medias_need_download = []
        for i, container in enumerate(containers):
            if container.download_check(overwrite=args.overwrite):
                containers_need_download.append(container)
                sign = "✓"
                print("{} {} qn: {}".format(sign, container.name, container.qn))
                for media in container.medias:
                    if media.download_check(overwrite=args.overwrite):
                        medias_need_download.append(media)
                        sign = "✓"
                        print("    {} {}".format(sign, media.name))
                    else:
                        sign = "✖"
                        print("    {} {}".format(sign, media.name))
            else:
                sign = "✖"
                print("{} {}".format(sign, container.name))

        aria2.download_video_list(map(lambda media: {
            "url": media.url,
            "filename": media.tmp_name
        }, medias_need_download), video_dir)
        for i, media in enumerate(medias_need_download):
            print("renaming {} {}/{}".format(media.name, i +
                                             1, len(medias_need_download)), end="\r")
            media.rename()
        for i, container in enumerate(containers_need_download):
            print("merging {} {}/{}".format(container.name, i +
                                            1, len(containers_need_download)), end="\r")
            container.merge(ffmpeg)
        print("已全部下载完成！")
    else:
        print("没有需要下载的视频！")

    # 弹幕转换为 ass 格式
    if args.danmaku == 'ass':
        convert_danmaku([
            container.path for container in containers
        ])
        print("转换完成")


if __name__ == "__main__":
    main()
