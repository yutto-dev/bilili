import re
import sys
import argparse


def main():
    """ 解析命令行参数并调用相关模块进行下载 """

    parser = argparse.ArgumentParser(description="bilili-dl")
    parser.add_argument("url", help="视频主页地址")
    parser.add_argument("-d", "--dir", default=r"", help="下载目录")
    parser.add_argument("-r", "--sharpness", default="112", choices=["112", "80", "64", "32", "16"],
                        help="视频清晰度 112:1080P+, 80:1080P, 64:720P, 32:480P, 16:360P")
    parser.add_argument("-t", "--num-thread", default="10", help="最大下载线程数")
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
        "num_thread": int(args.num_thread),
        "episodes": args.episodes,
        "playlist_type": args.playlist_type,
        "playlist_path_type": args.path_type.upper(),
        "ffmpeg_path": args.ffmpeg
    }

    if re.match(r"https?://www.bilibili.com/video/av(\d+)", args.url):
        import bili_video
        bili_video.start(args.url, config)
    elif re.match(r"https?://www.bilibili.com/bangumi/media/md(\d+)", args.url):
        import bili_bangumi
        bili_bangumi.start(args.url, config)
    else:
        print("视频地址有误！")
        sys.exit(1)


if __name__ == "__main__":
    main()
