import sys
import time

from bilili.utils.base import size_format
from bilili.utils.thread import ThreadPool, Flag
from bilili.utils.console import Console, Font, Line, String, ProgressBar, LineList, DynamicSymbol, ColorString
from bilili.tools import spider


class BiliDownloader:
    def __init__(self, containers, overwrite=False, debug=False, yes=False, num_threads=16, use_mirrors=False):
        self.overwrite = overwrite
        self.yes = yes
        self.debug = debug
        self.num_threads = num_threads
        self.use_mirrors = use_mirrors
        self.check_and_display(containers)
        self.download_pool, self.merge_pool, self.merge_wait_flag = self.init_tasks(containers)
        self.ui = self.init_ui()

    def check_and_display(self, containers):
        # 状态检查与校正
        for i, container in enumerate(containers):
            container_downloaded = not container.check_needs_download(self.overwrite)
            symbol = "✓" if container_downloaded else "✖"
            if container_downloaded:
                container._.merged = True
            print("{} {}".format(symbol, str(container)))
            for media in container.medias:
                media_downloaded = not media.check_needs_download(self.overwrite) or container_downloaded
                symbol = "✓" if media_downloaded else "✖"
                if not container_downloaded:
                    print("    {} {}".format(symbol, media.name))
                for block in media.blocks:
                    block_downloaded = not block.check_needs_download(self.overwrite) or media_downloaded
                    symbol = "✓" if block_downloaded else "✖"
                    block._.downloaded = block_downloaded
                    if not media_downloaded and self.debug:
                        print("        {} {}".format(symbol, block.name))

        # 询问是否下载，通过参数 -y 可以跳过
        if not self.yes:
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

    def init_tasks(self, containers):
        # 部署下载与合并任务
        merge_wait_flag = Flag(False)  # 合并线程池不能因为没有任务就结束
        # 因此要设定一个 flag，待最后合并结束后改变其值
        merge_pool = ThreadPool(3, wait=merge_wait_flag, daemon=True)
        download_pool = ThreadPool(
            self.num_threads,
            daemon=True,
            thread_globals_creator={
                "thread_spider": spider.clone  # 为每个线程创建一个全新的 Session，因为 requests.Session 不是线程安全的
                # https://github.com/psf/requests/issues/1871
            },
        )
        for container in containers:
            merging_file = MergingFile(
                container.type,
                [media.path for media in container.medias],
                container.path,
            )
            for media in container.medias:

                block_merging_file = MergingFile(None, [block.path for block in media.blocks], media.path)
                for block in media.blocks:

                    mirrors = block.mirrors if self.use_mirrors else []
                    remote_file = RemoteFile(block.url, block.path, mirrors=mirrors, range=block.range)

                    # 为下载挂载各种钩子，以修改状态，注意外部变量应当作为默认参数传入
                    @remote_file.on("before_download")
                    def before_download(file, status=block._):
                        status.downloading = True

                    @remote_file.on("updated")
                    def updated(file, status=block._):
                        status.size = file.size

                    @remote_file.on("downloaded")
                    def downloaded(
                        file, status=block._, merging_file=merging_file, block_merging_file=block_merging_file
                    ):
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
        return download_pool, merge_pool, merge_wait_flag

    def init_ui(self, debug=False):
        console = Console(debug=debug)
        console.add_component(Line(center=Font(char_a="𝓪", char_A="𝓐"), fillchar=" "))
        console.add_component(Line(left=ColorString(fore="cyan"), fillchar=" "))
        console.add_component(LineList(Line(left=String(), right=String(), fillchar="-")))
        console.add_component(
            Line(
                left=ColorString(
                    fore="green",
                    back="white",
                    subcomponent=ProgressBar(symbols=" ▏▎▍▌▋▊▉█", width=65),
                ),
                right=String(),
                fillchar=" ",
            )
        )
        console.add_component(Line(left=ColorString(fore="blue"), fillchar=" "))
        console.add_component(LineList(Line(left=String(), right=DynamicSymbol(symbols="🌑🌒🌓🌔🌕🌖🌗🌘"), fillchar=" ")))
        console.add_component(
            Line(
                left=ColorString(
                    fore="yellow",
                    back="white",
                    subcomponent=ProgressBar(symbols=" ▏▎▍▌▋▊▉█", width=65),
                ),
                right=String(),
                fillchar=" ",
            )
        )
        return console

    def run(self, containers):
        # 启动线程池
        self.merge_pool.run()
        self.download_pool.run()

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
            self.ui.refresh(
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
                self.merge_wait_flag.value = True
                self.download_pool.join()
                self.merge_pool.join()
                break
            try:
                # 将刷新率稳定在 2fps
                refresh_rate = 2
                time.sleep(max(1 / refresh_rate - (time.time() - now_t), 0.01))
            except (SystemExit, KeyboardInterrupt):
                raise
        print("已全部下载完成！")
