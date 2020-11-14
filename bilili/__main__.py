import sys

from bilili.utils.attrdict import AttrDict
from bilili.bootstrap.cli import parse_args
from bilili.bootstrap.parser import parse_containers
from bilili.bootstrap.downloader import BiliDownloader

if __name__ == "__main__":
    if (sys.version_info.major, sys.version_info.minor) < (3, 8):
        print("请使用 Python3.8 及以上版本哦～")
        sys.exit(1)

    options_list, global_options = parse_args()
    global_options = global_options >> AttrDict()
    containers = []
    for options in options_list:
        containers.extend(parse_containers(options))

    if containers:
        downloader = BiliDownloader(
            containers,
            overwrite=global_options.overwrite,
            debug=global_options.debug,
            yes=global_options.yes,
            num_threads=global_options.num_threads,
            use_mirrors=global_options.use_mirrors,
        )
        downloader.run(containers)
    else:
        print("没有需要下载的视频！")
