import os
import re
import time
import requests
import cv2

from utils.common import get_size, size_format, touch_dir, touch_file, Task
from utils.segment_dl import *
from utils.thread import ThreadPool
from utils.crawler import BililiCrawler


def parse_episodes(episodes_str, total):
    """ 将选集字符串转为列表 """

    # 解析字符串为列表
    print("全 {} 话".format(total))
    if episodes_str == "all":
        episode_list = list(range(1, total+1))
    elif re.match(r"\d+~\d+", episodes_str):
        start, end = episodes_str.split("~")
        start, end = int(start), int(end)
        assert end > start, "终点值应大于起点值"
        episode_list = list(range(start, end+1))
    elif re.match(r"\d+(,\d+)*", episodes_str):
        episode_list = episodes_str.split(",")
        episode_list = list(map(int, episode_list))
    else:
        episode_list = []

    # 筛选满足条件的剧集
    out_of_range = []
    episodes = []
    for episode in episode_list:
        if episode in range(1, total+1):
            if episode not in episodes:
                episodes.append(episode)
        else:
            out_of_range.append(episode)
    if out_of_range:
        print("warn: 剧集 {} 不存在".format(",".join(list(map(str, out_of_range)))))

    print("已选择第 {} 话".format(",".join(list(map(str, episodes)))))
    assert episodes, "没有选中任何剧集"
    return episodes


def convert_danmaku(video_path_list):
    """ 将视频文件夹下的 xml 弹幕转换为 ass 弹幕 """
    # 检测插件是否已经就绪
    plugin_url = "https://raw.githubusercontent.com/m13253/danmaku2ass/master/danmaku2ass.py"
    plugin_path = "plugins/danmaku2ass.py"
    touch_dir(os.path.dirname(plugin_path))
    touch_file(os.path.join(os.path.dirname(plugin_path), "__init__.py"))
    if not os.path.exists(plugin_path):
        print("下载插件中……")
        res = requests.get(plugin_url)
        with open(plugin_path, "w", encoding="utf8") as f:
            f.write(res.text)

    # 使用插件进行转换
    from plugins.danmaku2ass import Danmaku2ASS
    for video_path in video_path_list:
        name = os.path.splitext(video_path)[0]
        print("convert {} ".format(os.path.split(name)[-1]), end="\r")
        if not os.path.exists(name+".mp4") or \
                not os.path.exists(name+".xml"):
            continue
        cap = cv2.VideoCapture(name+".mp4")
        __, frame = cap.read()
        h, w, __ = frame.shape
        Danmaku2ASS(
            name+".xml", "autodetect", name+".ass",
            w, h, reserve_blank=0,
            font_face=_('(FONT) sans-serif')[7:],
            font_size=w/40, text_opacity=0.8, duration_marquee=15.0,
            duration_still=10.0, comment_filter=None, is_reduce_comments=False,
            progress_callback=None)


class BililiVideo():
    """ bilibili 单个视频类
    包括多个 B 站视频已经分好的段
    """

    def __init__(self, id, name, path, meta, segment_dl=True,
                segment_size=10*1024*1024, override=False, spider=BililiCrawler()):

        self.id = id
        self.name = name
        self.path = path
        self.meta = meta
        self.segment_dl = segment_dl
        self.segment_size = segment_size
        self.override = override
        self.spider = spider
        self.segments = []
        self.qn = 0
        self.total = 0
        self._status = INITIALIZED

    def __str__(self):
        """ 视频返回的字符串 """
        num_block = sum([len(segment.segments) for segment in self.segments])
        return "{} qn:{} {},{}".format(self.name, self.qn, len(self.segments))

    def switch_status(self, status=None):
        """ 切换到某一状态，默认为下一状态 """
        if status is None:
            self._status <<= 1
        else:
            self._status = status

    @property
    def size(self):
        """ 获取本地文件大小 """
        return sum([segment.size for segment in self.segments])

    @property
    def initialized(self):
        """ 返回状态字段是否是 INITIALIZED """
        return self._status == INITIALIZED

    @property
    def downloading(self):
        """ 返回状态字段是否是 DOWNLOADING """
        return self._status == DOWNLOADING

    @property
    def done(self):
        """ 返回状态字段是否是 DONE """
        return self._status == DONE


class BililiVideoSegment(NetworkFile):
    """ bilibili 单个视频片段类 """

    def __init__(self, id, path, url, qn, video):

        self.video = video
        super().__init__(url, path, video.segment_size, video.override, video.spider)
        self.id = id
        self.qn = qn
        self.video.qn = qn
        self.video.total += self.total

    def _segmentation(self):
        """ 分段，将各个片段添加至 self.segments """
        self.segmentable = self.segmentable and self.video.segment_dl
        if self.total and self.segmentable:
            for i in range(math.ceil(self.total/self.segment_size)):
                segment = BililiVideoBlock(self, i)
                self.segments.append(segment)
        else:
            segment = BililiVideoBlock(self, 0)
            self.segments.append(segment)


    @property
    def size(self):
        """ 获取本地文件大小 """
        if self.done:
            return self.total
        else:
            return sum([segment.size for segment in self.segments])


class BililiVideoBlock(Segment):
    """ bilibili 视频块类 """

    def __init__(self, video_segment, id):

        super().__init__(video_segment, id)
        self.video = self.file.video

    def download(self, ffmpeg):
        if self.video.initialized:
            self.video.switch_status()
        super().download()
        if self.file.done:
            if all([segment.done for segment in self.video.segments]):
                video_path_list = [segment.path
                                   for segment in self.video.segments]
                ffmpeg.join_videos(video_path_list, self.video.path)

                # 清除合并完成的视频片段
                for segment in self.video.segments:
                    os.remove(segment.path)

                self.video.switch_status()


class BiliFileManager():
    """ bilibili 文件管理器

    负责资源的分发与文件监控

    属性
        files: 待管理文件 List
        pool: 线程池
        override: 是否强制覆盖，默认不强制覆盖
        spider: 爬虫会话，requests.Session() 的封装
        segment_size: 片段大小，单位为字节
    """

    def __init__(self, num_thread, segment_size, ffmpeg, override=False):
        self.ffmpeg = ffmpeg
        self.videos = []
        self.pool = ThreadPool(num_thread)
        self.override = override
        self.segment_size = segment_size

    def dispense_resources(self, resources, log=True):
        """ 资源分发，将资源切分为片段，并分发至线程池 """

        for i, video in enumerate(resources):
            print("dispenser resources {}/{}".format(i, len(resources)), end="\r")
            if os.path.exists(video.path) and not self.override:
                sign = "!"
            else:
                sign = ">"
                self.videos.append(video)
                for segment in video.segments:
                    if os.path.exists(segment.path) and not self.override:
                        self.segment.switch_status(DONE)
                        continue
                    for block in segment.segments:
                        task = Task(block.download, args=(self.ffmpeg, ))
                        self.pool.add_task(task)
            if log:
                print("------{} {}".format(sign, video.name))

    def run(self):
        """ 启动任务 """
        self.pool.run()

    def monitoring(self):
        """ 启动监控器 """
        videos = self.videos
        size, t = sum([video.size for video in videos]), time.time()
        total_size = sum([video.total for video in videos])
        center_placeholder = "%(center)s"
        while len(videos):
            bar_length = 50
            max_length = 80
            log_string = " Downloading... ".center(max_length, "=") + "\n"

            # 下载速度
            now_size, now_t = sum([video.size for video in videos]), time.time()
            delta_size, delta_t = now_size - size, now_t - t
            size, t = now_size, now_t
            if delta_t < 1e-6:
                delta_t = 1e-6
            speed = delta_size / delta_t

            # 单个下载进度
            for video in videos:
                if video.downloading:
                    num_segment_done = sum(
                        [segment.done for segment in video.segments])
                    num_segment = len(video.segments)
                    if video.total:
                        line = "{}({}/{}) qn:{} {} {}/{}".format(video.name, num_segment_done, num_segment,
                                                         video.qn, center_placeholder, size_format(video.size),
                                                         size_format(video.total))
                    else:
                        line = "{}({}/{}) qn:{} {} {}".format(video.name, num_segment_done,
                                                      num_segment, video.qn, center_placeholder, size_format(video.size))
                    line = line.replace(center_placeholder, max(
                        max_length-len(line)+len(center_placeholder), 0)*"-")
                    log_string += line + "\n"

            # 下载进度
            if total_size != 0:
                len_done = bar_length * size // total_size
                len_undone = bar_length - len_done
                log_string += '{}{} {}/{} {:12}'.format("#" * len_done, "_" * len_undone,
                                                        size_format(size), size_format(
                                                            total_size),
                                                        size_format(speed)+"/s")
            else:
                num_done = sum([video.done for videos in videos])
                num_total = len(videos)
                len_done = bar_length * num_done // num_total
                len_undone = bar_length - len_done
                log_string += '{}{} {} {:12}'.format("#" * len_done, "_" * len_undone,
                                                     size_format(size), size_format(speed)+"/s")

            # 清空控制台并打印新的 log
            os.system('cls' if os.name == 'nt' else 'clear')
            print(log_string)

            # 监控是否全部完成
            if all([video.done for video in videos]):
                break

            try:
                time.sleep(max(1-(time.time()-now_t), 0.01))
            except (SystemExit, KeyboardInterrupt):
                raise

        # 清空控制台
        os.system('cls' if os.name == 'nt' else 'clear')
