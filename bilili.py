import re
import sys
import argparse

from utils import convert_danmaku
from common.base import Task
from common.ffmpeg import FFmpeg
from common.thread import ThreadPool


def main():
    """ 解析命令行参数并调用相关模块进行下载 """

    parser = argparse.ArgumentParser(description="bilili B 站视频、弹幕下载器")
    parser.add_argument("url", help="视频主页地址")
    parser.add_argument('-s', '--source', default='h5',
                        choices=['flash', 'h5', 'mp4'], help="选择播放源（html5 or flash or mp4）")
    parser.add_argument("-d", "--dir", default=r"", help="下载目录")
    parser.add_argument("-q", "--quality", default='120', choices=['120', '116', '112', '80', '74', '64', '32', '16'],
                        help="视频清晰度 112:1080P+, 80:1080P, 64:720P, 32:480P, 16:360P")
    parser.add_argument("-t", "--num-thread", default=30,
                        type=int, help="最大下载线程数")
    parser.add_argument("-p", "--episodes", default="all", help="选集")
    parser.add_argument("-w", "--overwrite",
                        action="store_true", help="强制覆盖已下载视频")
    parser.add_argument("-c", "--sess-data", default=None, help="输入 cookies")
    parser.add_argument("--ass", action="store_true",
                        help="自动将 xml 弹幕转换为 ass 弹幕")
    parser.add_argument("--enable-block", action="store_true", help="启用分段下载")
    parser.add_argument("--playlist-type", default="dpl",
                        choices=["dpl", "m3u", "no"], help="播放列表类型，支持 dpl 和 m3u，输入 no 不生成播放列表")
    parser.add_argument("--path-type", default="rp",
                        help="播放列表路径类型（rp：相对路径，ap：绝对路径）")
    parser.add_argument("--block-size", default=128*1024*1024, type=int,
                        help="分段下载器的块大小，默认为 128MB")

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
        "block_size": args.block_size,
        "cookies": cookies,
        "segmentation": args.enable_block,
    }

    if args.source.lower() == 'h5':
        import bilibili_h5 as bili
    elif args.source.lower() == 'mp4':
        import bilibili_mp4 as bili
    else:
        import bilibili as bili

    if re.match(r"https?://www.bilibili.com/video/av(\d+)", args.url) or \
            re.match(r"https?://b23.tv/av(\d+)", args.url) or \
            re.match(r"https?://www.bilibili.com/video/BV(\w+)", args.url) or \
            re.match(r"https?://b23.tv/BV(\w+)", args.url):
        if args.source.lower() == 'h5':
            import bilibili_h5.acg_video as bilili
        elif args.source.lower() == 'mp4':
            import bilibili_mp4.acg_video as bilili
        else:
            import bilibili.acg_video as bilili
    elif re.match(r"https?://www.bilibili.com/bangumi/media/md(\d+)", args.url):
        if args.source.lower() == 'h5':
            import bilibili_h5.bangumi as bilili
        elif args.source.lower() == 'mp4':
            print("番剧不支持 MP4 解析哦")
            sys.exit(0)
        else:
            import bilibili.bangumi as bilili
    else:
        print("视频地址有误！")
        sys.exit(1)

    # 解析资源
    bilili.parse(args.url, config)

    if bilili.exports["videos"]:
        # 创建文件管理器，并分发任务
        ffmpeg = FFmpeg()
        manager = bili.downloader.BiliFileManager(
            args.num_thread, 1024*1024, ffmpeg, args.overwrite)
        # 启动并监控任务
        manager.dispense_resources(bilili.exports["videos"])
        manager.run()
        manager.monitoring()
        print("已全部下载完成！")
    else:
        print("没有需要下载的视频！")

    # 弹幕转换为 ass 格式
    if args.ass:
        convert_danmaku([
            video.path for video in bilili.exports["videos"]
        ])
        print("转换完成")


if __name__ == "__main__":
    main()
