import re
import sys
import argparse

from common import download_segment, manager
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
    parser.add_argument("-t", "--num-thread", default=10,
                        type=int, help="最大下载线程数")
    parser.add_argument("-p", "--episodes", default="all", help="最大下载线程数")
    parser.add_argument("--playlist-type", default="dpl",
                        choices=["dpl", "m3u", "no"], help="播放列表类型，支持 dpl 和 m3u，输入 no 不生成播放列表")
    parser.add_argument("--path-type", default="rp",
                        help="播放列表路径类型（rp：相对路径，ap：绝对路径）")
    parser.add_argument("--ffmpeg", default="ffmpeg/ffmpeg.exe",
                        help="ffmpeg 路径")

    args = parser.parse_args()
    # 高清 1080P+ 高清 1080P  高清 720P  清晰 480P  流畅 360P
    sps = [112, 80, 64, 32, 16]

    config = {
        "url": args.url,
        "dir": args.dir,
        "sp_seq": sps[sps.index(int(args.sharpness)):] + list(reversed(sps[:sps.index(int(args.sharpness))])),
        "episodes": args.episodes,
        "playlist_type": args.playlist_type,
        "playlist_path_type": args.path_type.upper(),
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

    # 创建下载线程池，准备下载
    pool = ThreadPool(args.num_thread)
    ffmpeg = FFmpeg(args.ffmpeg)

    # 为线程池添加下载任务
    for item in bilili.exports["info"]:
        for segment in item["segments"]:
            pool.add_task(
                Task(download_segment, (segment, item, bilili.exports["spider"], ffmpeg)))

    # 启动下载线程池
    pool.run()

    # 主线程监控
    manager(bilili.exports["info"], bilili.exports["video_dir"])


if __name__ == "__main__":
    main()
