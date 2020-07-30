import re
import sys
import argparse
import os
import json

from utils import parse_episodes, convert_danmaku
from common.base import repair_filename, touch_dir, remove
from common.playlist import Dpl, M3u
from api.subtitle import get_subtitle
from api.danmaku import get_danmaku
from tools import aria2, ffmpeg, spider


def main():
    """ 解析命令行参数并调用相关模块进行下载 """

    parser = argparse.ArgumentParser(description="bilili B 站视频、弹幕下载器")
    parser.add_argument("url", help="视频主页地址")
    parser.add_argument('-f', '--format', default='m4s',
                        choices=['flv', 'm4s', 'mp4'], help="选择播放源（html5 or flash or mp4）")
    parser.add_argument("-d", "--dir", default=r"", help="下载目录")
    parser.add_argument("-q", "--quality", default='120', choices=['120', '116', '112', '80', '74', '64', '32', '16', '6'],
                        help="视频清晰度 112:1080P+, 80:1080P, 64:720P, 32:480P, 16:360P")
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

    if re.match(r"https?://www.bilibili.com/video/av(\d+)", args.url) or \
            re.match(r"https?://b23.tv/av(\d+)", args.url) or \
            re.match(r"https?://www.bilibili.com/video/BV(\w+)", args.url) or \
            re.match(r"https?://b23.tv/BV(\w+)", args.url):
        bili_type = "acg_video"
        from api.acg_video import get_title, get_context, get_containers, parse_segments
    elif re.match(r"https?://www.bilibili.com/bangumi/media/md(\d+)", args.url):
        bili_type = "bangumi"
        from api.bangumi import get_title, get_context, get_containers, parse_segments
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
    if args.ass:
        convert_danmaku([
            container.path for container in containers
        ])
        print("转换完成")


if __name__ == "__main__":
    main()
