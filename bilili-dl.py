import re
import argparse


def main():
    """ 解析命令行参数并调用相关模块进行下载 """

    parser = argparse.ArgumentParser(description='bilili-dl')
    parser.add_argument('url', help='视频主页地址')
    parser.add_argument('-d', default=r'', help='下载目录')
    parser.add_argument('-r', default='80', help='视频清晰度 80:超清，64:高清，32:标清，16:流畅')
    parser.add_argument('-t', default='10', help='最大下载线程数')
    parser.add_argument('--playlist-type', default='dpl', help='播放列表类型，支持 dpl 和 m3u')
    parser.add_argument('--path-type', default='rp', help='播放列表路径类型（rp：相对路径，ap：绝对路径）')
    parser.add_argument('--ffmpeg', default='ffmpeg/ffmpeg.exe',
                        help='ffmpeg 路径')

    args = parser.parse_args()
    sps = [80, 64, 32, 16]  # 高清 1080P  高清 720P  清晰 480P  流畅 360P

    config = {
        "url": args.url,
        "dir": args.d,
        "sp_seq": sps[sps.index(int(args.r)):] + list(reversed(sps[:sps.index(int(args.r))])),
        "num_thread": int(args.t),
        "playlist_type": args.playlist_type,
        "playlist_path_type": args.path_type.upper(),
        "ffmpeg_path": args.ffmpeg
    }

    if re.match(r'https?://www.bilibili.com/video/av(\d+)', args.url):
        import bili_video
        bili_video.start(args.url, config)
    elif re.match(r'https?://www.bilibili.com/bangumi/media/md(\d+)', args.url):
        import bili_bangumi
        bili_bangumi.start(args.url, config)
    else:
        print('视频地址有误！')
        sys.exit(1)


if __name__ == '__main__':
    main()
