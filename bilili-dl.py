import re
import sys
import argparse

from common import convert_danmaku, BiliFileManager
from utils.common import Task
from utils.ffmpeg import FFmpeg
from utils.thread import ThreadPool


def main():
    """ 解析命令行参数并调用相关模块进行下载 """

    parser = argparse.ArgumentParser(description="bilili-dl")
    parser.add_argument("url", help="视频主页地址")
    parser.add_argument("-d", "--dir", default=r"", help="下载目录")
    parser.add_argument("-r", "--sharpness", default="112", choices=["112", "80", "64", "32", "16"],
                        help="视频清晰度 112:1080P+, 80:1080P, 64:720P, 32:480P, 16:360P")
    parser.add_argument("-t", "--num-thread", default=30,
                        type=int, help="最大下载线程数")
    parser.add_argument("-p", "--episodes", default="all", help="选集")
    parser.add_argument("-w", "--override",
                        action="store_true", help="强制覆盖已下载视频")
    parser.add_argument("-c", "--sess-data", default=None, help="输入 cookies")
    parser.add_argument("--ass", action="store_true",
                        help="自动将 xml 弹幕转换为 ass 弹幕")
    parser.add_argument("--no-block", action="store_false", help="不使用分段下载")
    parser.add_argument("--playlist-type", default="dpl",
                        choices=["dpl", "m3u", "no"], help="播放列表类型，支持 dpl 和 m3u，输入 no 不生成播放列表")
    parser.add_argument("--path-type", default="rp",
                        help="播放列表路径类型（rp：相对路径，ap：绝对路径）")
    parser.add_argument("--segment-size", default=4*1024*1024, type=int,
                        help="分段下载器的块大小，默认为 3MB")
    parser.add_argument("--ffmpeg", default="ffmpeg/ffmpeg.exe",
                        help="ffmpeg 路径")

    args = parser.parse_args()
    # 超清 4K 高清 1080P60 高清 1080P+ 高清 1080P  高清 720P60 高清 720P  清晰 480P  流畅 360P
    qns = [120, 116, 112, 80, 74, 64, 32, 16]
    cookies = {
        "SESSDATA": args.sess_data
    }

    config = {
        "url": args.url,
        "dir": args.dir,
        "qn_seq": qns[qns.index(int(args.sharpness)):] + list(reversed(qns[:qns.index(int(args.sharpness))])),
        "episodes": args.episodes,
        "playlist_type": args.playlist_type,
        "playlist_path_type": args.path_type.upper(),
        "override": args.override,
        "segment_size": args.segment_size,
        "cookies": cookies,
        "segment_dl": args.no_block,
    }

    if re.match(r"https?://www.bilibili.com/video/av(\d+)", args.url):
        import bili_video as bilili
    elif re.match(r"https?://www.bilibili.com/bangumi/media/md(\d+)", args.url):
        import bili_bangumi as bilili
    else:
        print("视频地址有误！")
        sys.exit(1)

    # 解析资源
    bilili.parse(args.url, config)

    if bilili.exports["videos"]:
        # 创建文件管理器，并分发任务
        ffmpeg = FFmpeg(args.ffmpeg)
        manager = BiliFileManager(
            args.num_thread, 1024*1024, ffmpeg, args.override)
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
