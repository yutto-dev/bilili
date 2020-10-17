import re
import sys
import argparse
import os
import time

from typing import List
from bilili.utils.base import repair_filename, touch_dir, touch_file, size_format
from bilili.utils.playlist import Dpl, M3u
from bilili.utils.thread import ThreadPool, Flag
from bilili.utils.console import (Console, Font, Line, String, ProgressBar,
                                  LineList, DynamicSymbol, ColorString)
from bilili.utils.subtitle import Subtitle
from bilili.utils.attrdict import AttrDict
from bilili.tools import spider, ass, regex
from bilili.tools import global_status
from bilili.handlers.downloader import RemoteFile
from bilili.handlers.merger import MergingFile
from bilili.video import BililiContainer
from bilili.api.subtitle import get_subtitle
from bilili.api.danmaku import get_danmaku
from bilili.api.exceptions import (ArgumentsError, CannotDownloadError,
                                   UnknownTypeError, UnsupportTypeError, IsPreviewError)


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


def main():
    """ 解析命令行参数并调用相关模块进行下载 """

    if (sys.version_info.major, sys.version_info.minor) < (3, 8):
        print("请使用 Python3.8 及以上版本哦～")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="bilili B 站视频、弹幕下载器")
    parser.add_argument("url", help="视频主页地址")
    parser.add_argument(
        "-t", "--type", default="dash", choices=["flv", "dash", "mp4"], help="选择下载源类型（dash 或 flv 或 mp4）",
    )
    parser.add_argument("-d", "--dir", default=r"", help="下载目录")
    parser.add_argument(
        "-q",
        "--quality",
        default=120,
        choices=[120, 116, 112, 80, 74, 64, 32, 16],
        type=int,
        help="视频清晰度 120:4K, 116:1080P60, 112:1080P+, 80:1080P, 74:720P60, 64:720P, 32:480P, 16:360P",
    )
    parser.add_argument("-n", "--num-threads", default=16, type=int, help="最大下载线程数")
    parser.add_argument("-p", "--episodes", default="^~$", help="选集")
    parser.add_argument("-w", "--overwrite", action="store_true", help="强制覆盖已下载视频")
    parser.add_argument("-c", "--sess-data", default=None, help="输入 cookies")
    parser.add_argument("-y", "--yes", action="store_true", help="跳过下载询问")
    parser.add_argument(
        "--audio-quality", default=30280,
        choices=[30280, 30232, 30216],
        type=int,
        help="音频码率等级 30280:320kbps, 30232:128kbps, 30216:64kbps",
    )
    parser.add_argument(
        "--playlist-type", default="dpl", choices=["dpl", "m3u", "no"], help="播放列表类型，支持 dpl 和 m3u，输入 no 不生成播放列表",
    )
    parser.add_argument(
        "--danmaku", default="xml", choices=["xml", "ass", "no"], help="弹幕类型，支持 xml 和 ass，如果设置为 no 则不下载弹幕",
    )
    parser.add_argument(
        "--block-size", default=128, type=int, help="分块下载器的块大小，单位为 MB，默认为 128MB，设置为 0 时禁用分块下载",
    )
    parser.add_argument("--abs-path", action="store_true", help="修改播放列表路径类型为绝对路径")
    parser.add_argument("--use-mirrors", action="store_true", help="启用从多个镜像下载功能")
    parser.add_argument("--disable-proxy", action="store_true", help="禁用系统代理")
    parser.add_argument("--debug", action="store_true", help="debug 模式")

    args = parser.parse_args()
    cookies = {"SESSDATA": args.sess_data}

    config = {
        "url": args.url,
        "dir": args.dir,
        "quality": args.quality,
        "audio_quality": args.audio_quality,
        "episodes": args.episodes,
        "playlist_type": args.playlist_type,
        "playlist_path_type": "AP" if args.abs_path else "RP",
        "overwrite": args.overwrite,
        "cookies": cookies,
        "type": args.type.lower(),
        "block_size": int(args.block_size * 1024 * 1024),
    } >> AttrDict()

    # 匹配资源的 id 以及其对应所属类型
    # fmt: off
    resource_id = {
        "avid": "",
        "bvid": "",
        "episode_id": "",
        "season_id": "",
    } >> AttrDict()

    # fmt: off
    if (avid_match := regex.acg_video.av.origin.match(args.url)) or \
        (avid_match := regex.acg_video.av.short.match(args.url)):
        from bilili.api.acg_video import get_video_info
        avid = avid_match.group("avid")
        if episode_id := get_video_info(avid=avid)["episode_id"]:
            resource_id.episode_id = episode_id
        else:
            resource_id.avid = avid
    elif (bvid_match := regex.acg_video.bv.origin.match(args.url)) or \
        (bvid_match := regex.acg_video.bv.short.match(args.url)):
        from bilili.api.acg_video import get_video_info
        bvid = bvid_match.group("bvid")
        if episode_id := get_video_info(bvid=bvid)["episode_id"]:
            resource_id.episode_id = episode_id
        else:
            resource_id.bvid = bvid
    elif media_id_match := regex.bangumi.md.origin.match(args.url):
        from bilili.api.bangumi import get_season_id
        media_id = media_id_match.group("media_id")
        resource_id.season_id = get_season_id(media_id=media_id)
    elif (episode_id_match := regex.bangumi.ep.origin.match(args.url)) or \
        (episode_id_match := regex.bangumi.ep.short.match(args.url)):
        episode_id = episode_id_match.group("episode_id")
        resource_id.episode_id = episode_id
    elif (season_id_match := regex.bangumi.ss.origin.match(args.url)) or \
        (season_id_match := regex.bangumi.ss.short.match(args.url)):
        season_id = season_id_match.group("season_id")
        resource_id.season_id = season_id
    else:
        print("视频地址有误！")
        sys.exit(1)

    if resource_id.avid or resource_id.bvid:
        from bilili.parser.acg_video import get_title, get_list, get_playurl
        bili_type = "acg_video"
    elif resource_id.season_id or resource_id.episode_id:
        from bilili.parser.bangumi import get_title, get_list, get_playurl
        bili_type = "bangumi"

    # 获取标题
    spider.set_cookies(config["cookies"])
    if args.disable_proxy:
        spider.trust_env = False
    title = get_title(resource_id)
    print(title)

    # 创建所需目录结构
    base_dir = touch_dir(os.path.join(config["dir"], repair_filename(title + " - bilibili")))
    video_dir = touch_dir(os.path.join(base_dir, "Videos"))

    # 获取需要的信息
    containers = [BililiContainer(video_dir=video_dir, type=args.type, **video) for video in get_list(resource_id)]

    # 解析并过滤不需要的选集
    episodes = parse_episodes(config["episodes"], len(containers))
    containers, containers_need_filter = [], containers
    for container in containers_need_filter:
        if container.id not in episodes:
            container._.downloaded = True
            container._.merged = True
        else:
            containers.append(container)

    # 初始化播放列表
    if config["playlist_type"] == "dpl":
        playlist = Dpl(os.path.join(base_dir, "Playlist.dpl"), path_type=config["playlist_path_type"])
    elif config["playlist_type"] == "m3u":
        playlist = M3u(os.path.join(base_dir, "Playlist.m3u"), path_type=config["playlist_path_type"])
    else:
        playlist = None

    # 解析片段信息及视频 url
    for i, container in enumerate(containers):
        print(
            "{:02}/{:02} parsing segments info...".format(i + 1, len(containers)), end="\r",
        )

        # 解析视频 url
        try:
            for playinfo in get_playurl(container, config["quality"], config["audio_quality"]):
                container.append_media(
                    block_size=config["block_size"],
                    **playinfo
                )
        except CannotDownloadError as e:
            print('[warn] {} 无法下载，原因：{}'.format(container.name, e.message))
        except IsPreviewError:
            print('[warn] {} 是预览视频'.format(container.name))

        # 写入播放列表
        if playlist is not None:
            playlist.write_path(container.path)

        # 下载弹幕
        if bili_type == "acg_video":
            for sub_info in get_subtitle(avid=resource_id.avid, bvid=resource_id.bvid, cid=container.meta['cid']):
                sub_path = '{}_{}.srt'.format(os.path.splitext(container.path)[0], sub_info['lang'])
                subtitle = Subtitle(sub_path)
                for sub_line in sub_info['lines']:
                    subtitle.write_line(sub_line["content"], sub_line["from"], sub_line["to"])

        # 生成弹幕
        if args.danmaku != "no":
            with open(os.path.splitext(container.path)[0] + ".xml", 'w', encoding='utf-8') as f:
                f.write(get_danmaku(container.meta['cid']))

        # 转换弹幕为 ASS
        if args.danmaku == "ass":
            ass.convert_danmaku_from_xml(
                os.path.splitext(container.path)[0] + ".xml", container.height, container.width,
            )
    if playlist is not None:
        playlist.flush()

    # 准备下载
    if containers:
        # 状态检查与校正
        for i, container in enumerate(containers):
            container_downloaded = not container.check_needs_download(args.overwrite)
            symbol = "✓" if container_downloaded else "✖"
            if container_downloaded:
                container._.merged = True
            print("{} {}".format(symbol, str(container)))
            for media in container.medias:
                media_downloaded = not media.check_needs_download(args.overwrite) or container_downloaded
                symbol = "✓" if media_downloaded else "✖"
                if not container_downloaded:
                    print("    {} {}".format(symbol, media.name))
                for block in media.blocks:
                    block_downloaded = not block.check_needs_download(args.overwrite) or media_downloaded
                    symbol = "✓" if block_downloaded else "✖"
                    block._.downloaded = block_downloaded
                    if not media_downloaded and args.debug:
                        print("        {} {}".format(symbol, block.name))

        # 询问是否下载，通过参数 -y 可以跳过
        if not args.yes:
            answer = None
            while answer is None:
                result = input("以上标 ✖ 为需要进行下载的视频，是否立刻进行下载？[Y/n]")
                if result == "" or result[0].lower() == "y":
                    answer = True
                elif result[0].lower() == "n":
                    answer = False
                else:
                    answer = None
            if not answer:
                sys.exit(0)

        # 部署下载与合并任务
        merge_wait_flag = Flag(False)  # 合并线程池不能因为没有任务就结束
        # 因此要设定一个 flag，待最后合并结束后改变其值
        merge_pool = ThreadPool(3, wait=merge_wait_flag, daemon=True)
        download_pool = ThreadPool(args.num_threads, daemon=True, thread_globals_creator={
            "thread_spider":spider.clone            # 为每个线程创建一个全新的 Session，因为 requests.Session 不是线程安全的
                                                    # https://github.com/psf/requests/issues/1871
        })
        for container in containers:
            merging_file = MergingFile(container.type, [media.path for media in container.medias], container.path,)
            for media in container.medias:

                block_merging_file = MergingFile(None, [block.path for block in media.blocks], media.path)
                for block in media.blocks:

                    mirrors = block.mirrors if args.use_mirrors else []
                    remote_file = RemoteFile(block.url, block.path, mirrors=mirrors, range=block.range)

                    # 为下载挂载各种钩子，以修改状态，注意外部变量应当作为默认参数传入
                    @remote_file.on("before_download")
                    def before_download(file, status=block._):
                        status.downloading = True

                    @remote_file.on("updated")
                    def updated(file, status=block._):
                        status.size = file.size

                    @remote_file.on("downloaded")
                    def downloaded(file, status=block._, merging_file=merging_file, block_merging_file=block_merging_file):
                        status.downloaded = True

                        if status.parent.downloaded:
                            # 当前 media 的最后一个 block 所在线程进行合并（直接执行，不放线程池）
                            status.downloaded = False
                            block_merging_file.merge()
                            status.downloaded = True

                            # 如果该线程同时也是当前 container 的最后一个 block，就部署合并任务（放到线程池）
                            if status.parent.parent.downloaded and not status.parent.parent.merged:
                                # 为合并挂载各种钩子
                                @merging_file.on("before_merge")
                                def before_merge(file, status=status.parent.parent):
                                    status.merging = True

                                @merging_file.on("merged")
                                def merged(file, status=status.parent.parent):
                                    status.merging = False
                                    status.merged = True

                                merge_pool.add_task(merging_file.merge, args=())

                        status.downloading = False

                    # 下载过的不应继续部署任务
                    if block._.downloaded:
                        continue
                    download_pool.add_task(remote_file.download, args=())

        # 启动线程池
        merge_pool.run()
        download_pool.run()

        # 初始化界面
        console = Console(debug=args.debug)
        console.add_component(Line(center=Font(char_a="𝓪", char_A="𝓐"), fillchar=" "))
        console.add_component(Line(left=ColorString(fore="cyan"), fillchar=" "))
        console.add_component(LineList(Line(left=String(), right=String(), fillchar="-")))
        console.add_component(
            Line(
                left=ColorString(fore="green", back="white", subcomponent=ProgressBar(symbols=" ▏▎▍▌▋▊▉█", width=65),),
                right=String(),
                fillchar=" ",
            )
        )
        console.add_component(Line(left=ColorString(fore="blue"), fillchar=" "))
        console.add_component(LineList(Line(left=String(), right=DynamicSymbol(symbols="🌑🌒🌓🌔🌕🌖🌗🌘"), fillchar=" ")))
        console.add_component(
            Line(
                left=ColorString(fore="yellow", back="white", subcomponent=ProgressBar(symbols=" ▏▎▍▌▋▊▉█", width=65),),
                right=String(),
                fillchar=" ",
            )
        )

        # 准备监控
        size, t = global_status.size, time.time()
        while True:
            now_size, now_t = global_status.size, time.time()
            delta_size, delta_t = (
                max(now_size - size, 0),
                (now_t - t) if now_t - t > 1e-6 else 1e-6,
            )
            speed = delta_size / delta_t
            size, t = now_size, now_t

            # 数据传入，界面渲染
            console.refresh(
                # fmt: off
                [
                    {
                        "center": " 🍻 bilili ",
                    },
                    {
                        "left": "🌠 Downloading videos: "
                    } if global_status.downloading else None,
                    [
                        {
                            "left": "{} ".format(str(container)),
                            "right": " {}/{}".format(
                                size_format(container._.size), size_format(container._.total_size),
                            ),
                        } if container._.downloading else None
                        for container in containers
                    ] if global_status.downloading else None,
                    {
                        "left": global_status.size / global_status.total_size,
                        "right": " {}/{} {}/s ⚡".format(
                            size_format(global_status.size),
                            size_format(global_status.total_size),
                            size_format(speed),
                        ),
                    } if global_status.downloading else None,
                    {
                        "left": "🍰 Merging videos: "
                    } if global_status.merging else None,
                    [
                        {
                            "left": "{} ".format(str(container)),
                            "right": True
                        } if container._.merging else None
                        for container in containers
                    ] if global_status.merging else None,
                    {
                        "left": sum([container._.merged for container in containers]) / len(containers),
                        "right": " {}/{} 🚀".format(
                            sum([container._.merged for container in containers]), len(containers),
                        ),
                    } if global_status.merging else None,
                ]
            )

            # 检查是否已经全部完成
            if global_status.downloaded and global_status.merged:
                merge_wait_flag.value = True
                download_pool.join()
                merge_pool.join()
                break
            try:
                # 将刷新率稳定在 2fps
                refresh_rate = 2
                time.sleep(max(1 / refresh_rate - (time.time() - now_t), 0.01))
            except (SystemExit, KeyboardInterrupt):
                raise
        print("已全部下载完成！")
    else:
        print("没有需要下载的视频！")


if __name__ == "__main__":
    main()
