import re
import sys
import argparse

from typing import List, Tuple

OPTIONS = [
    "uri",
    "type",
    "dir",
    "quality",
    "num_threads",  # 仅全局
    "episodes",
    "overwrite",  # 仅全局
    "sess_data",  # 仅全局
    "yes",  # 仅全局
    "audio_quality",
    "playlist_type",
    "danmaku",
    "block_size",  # 仅全局
    "abs_path",
    "use_mirrors",  # 仅全局
    "disable_proxy",  # 仅全局
    "debug",  # 仅全局
]


def get_parser():
    parser = argparse.ArgumentParser(description="bilili B 站视频、弹幕下载器")
    parser.add_argument("uri", nargs="?", default=sys.stdin, help="视频主页地址")
    parser.add_argument(
        "-t",
        "--type",
        default="dash",
        choices=["flv", "dash", "mp4"],
        help="选择下载源类型（dash 或 flv 或 mp4）",
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
        "--audio-quality",
        default=30280,
        choices=[30280, 30232, 30216],
        type=int,
        help="音频码率等级 30280:320kbps, 30232:128kbps, 30216:64kbps",
    )
    parser.add_argument(
        "--playlist-type",
        default="dpl",
        choices=["dpl", "m3u", "no"],
        help="播放列表类型，支持 dpl 和 m3u，输入 no 不生成播放列表",
    )
    parser.add_argument(
        "--danmaku",
        default="xml",
        choices=["xml", "ass", "no"],
        help="弹幕类型，支持 xml 和 ass，如果设置为 no 则不下载弹幕",
    )
    parser.add_argument(
        "--block-size",
        default=128,
        type=int,
        help="分块下载器的块大小，单位为 MB，默认为 128MB，设置为 0 时禁用分块下载",
    )
    parser.add_argument("--abs-path", action="store_true", help="修改播放列表路径类型为绝对路径")
    parser.add_argument("--use-mirrors", action="store_true", help="启用从多个镜像下载功能")
    parser.add_argument("--disable-proxy", action="store_true", help="禁用系统代理")
    parser.add_argument("--debug", action="store_true", help="debug 模式")
    return parser


def parse_text_options(text):
    # TODO: 支持 JSON、YAML 的解析
    allow_options = list(OPTIONS)
    for exclude_option in [
        "num_threads",
        "overwrite",
        "sess_data",
        "yes",
        "block_size",
        "use_mirrors",
        "disable_proxy",
        "debug",
    ]:
        allow_options.pop(allow_options.index(exclude_option))
    options_list = []
    for line in text.split("\n"):
        if not line or re.match(r"^\s+$", line):
            pass
        elif line.startswith(" ") or line.startswith("\t"):
            option, value = re.split(r"\s", line.lstrip())[:2]
            if option in allow_options:
                if option in ["quality", "audio_quality"]:
                    value = int(value)
                if option in ["abs_path", "overwrite"]:
                    value = {"true": True, "false": False}[value.lower()]
                options_list[-1][option] = value
            else:
                print("Warning: 局部作用域无效的选项 {}".format(option))
        else:
            options = {}
            options["uri"] = line.strip()
            options_list.append(options)
    return options_list


def parse_args() -> Tuple[List[object], object]:
    """解析参数，返回选项列表

    Returns:
        List[object]: 选项列表，每个选项包含一个目标地址
    """
    parser = get_parser()
    args = parser.parse_args()

    global_options = {option: getattr(args, option) for option in OPTIONS}

    options_list = []

    if isinstance(args.uri, str):
        if re.match(r"https?://", args.uri):
            options = dict(global_options)
            options.update(
                {
                    "uri": args.uri,
                }
            )
            options_list = [options]
        elif re.match(r"file://", args.uri):
            filepath = args.uri[7:]
            # TODO: 支持相对路径
            with open(filepath, "r", encoding="utf-8") as f:
                text_options = f.read()
                options_list = parse_text_options(text_options)
                for i, options in enumerate(options_list):
                    options_list[i] = dict(global_options)
                    options_list[i].update(options)
        else:
            print("Error: 不规范的 uri 参数")
            sys.exit(1)
    else:
        text_options = args.uri.read()
        options_list = parse_text_options(text_options)
        for i, options in enumerate(options_list):
            options_list[i] = dict(global_options)
            options_list[i].update(options)
        global_options["yes"] = True  # 由于此时无法输入，因此直接默认确认

    return options_list, global_options
