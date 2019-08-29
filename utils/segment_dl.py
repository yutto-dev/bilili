import os
import re
import time
import math

from utils.common import Task, size_format
from utils.crawler import Crawler
from utils.thread import ThreadPool


INITIALIZED = 1
DOWNLOADING = 2
DONE = 4


class NetworkFile():
    """ 网络文件类，对应一个网络文件资源

    属性
        url: 文件的网络地址
        path: 文件的本地存储路径
        name: 文件的名称
        segment_size: 单个片段的大小，单位为字节，默认 10MB
        override: 是否强制覆盖，默认不强制覆盖
        spider: 爬虫会话，requests.Session() 的封装
        size: 本地已下载部分大小
        initialized: 文件是否处于刚刚初始化的状态
        downloading: 文件是否处于下载中的状态
        done: 文件是否处于下载完成的状态
        segmentabel: 文件是否允许分段下载
        total: 文件的完整大小
        segments: 文件片段 List
    """

    def __init__(self, url, path, segment_size=10*1024*1024,
                 override=False, spider=Crawler()):
        self.url = url
        self.path = path
        self.name = os.path.split(self.path)[-1]
        self.override = override
        self.spider = spider
        self.segment_size = segment_size
        self._status = INITIALIZED
        self.segmentable = False
        self.total = 0
        self.segments = []
        self._get_head()
        self._segmentation()

    def _get_head(self):
        """ 连接测试，获取文件大小与是否可分段 """
        headers = dict(self.spider.headers)
        headers['Range'] = 'bytes=0-4'
        try:
            res = self.spider.head(
                self.url, headers=headers, allow_redirects=True, timeout=20)
            crange = res.headers['Content-Range']
            self.total = int(re.match(r'^bytes 0-4/(\d+)$', crange).group(1))
            self.segmentable = True
            return
        except:
            self.segmentable = False
        try:
            res = self.spider.head(self.url, allow_redirects=True, timeout=20)
            self.total = int(res.headers['Content-Length'])
        except:
            self.total = 0

    def _segmentation(self):
        """ 分段，将各个片段添加至 self.segments """
        if self.total and self.segmentable:
            for i in range(math.ceil(self.total/self.segment_size)):
                segment = Segment(self, i)
                self.segments.append(segment)
        else:
            segment = Segment(self, 0)
            self.segments.append(segment)

    def merge(self):
        """ 合并各个片段 """
        with open(self.path, "wb") as fw:
            for segment in self.segments:
                with open(segment.path, "rb") as fr:
                    fw.write(fr.read())
                segment.remove()

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


class Segment():
    """ 网络片段类，对应一个网络文件片段

    属性
        file: 片段所在的文件类
        path: 片段的本地存储路径
        name: 片段的名称
        tmp_path: 片段的临时文件存储路径
        id: 片段在一个文件中的唯一标志号
        size: 本地已下载部分大小
        initialized: 文件是否处于刚刚初始化的状态
        downloading: 文件是否处于下载中的状态
        done: 文件是否处于下载完成的状态
    """

    def __init__(self, file, id):
        self.file = file
        self.path = "{}.{:06}".format(file.path, id)
        self.name = os.path.split(self.path)[-1]
        self.tmp_path = self.path + "t"
        self.id = id
        self._status = INITIALIZED
        self.size = 0

    def download(self, stream=True, chunk_size=1024):
        """ 下载片段 """

        # 更改状态
        self.switch_status()
        if self.file.initialized:
            self.file.switch_status()

        if self.file.override:
            self.remove()
        self.size = self.get_size()
        if not os.path.exists(self.path):
            # 设置 headers
            headers = dict(self.file.spider.headers)
            if self.file.segmentable and self.file.total:
                headers["Range"] = "bytes={}-{}".format(
                    self.id * self.file.segment_size + self.size,
                    (self.id+1) * self.file.segment_size - 1)
            elif self.file.total:
                headers["Range"] = "bytes={}-".format(
                    self.id * self.file.segment_size + self.size)

            # 建立连接并下载
            connected = False
            while not connected:
                try:
                    res = self.file.spider.get(
                        self.file.url, stream=True, headers=headers)
                    connected = True
                except:
                    print("[warn] content failed, try again...")
            with open(self.tmp_path, 'ab') as f:
                if stream:
                    for chunk in res.iter_content(chunk_size=chunk_size):
                        if not chunk:
                            break
                        f.write(chunk)
                        self.size += len(chunk)
                else:
                    f.write(res.content)

            # 从临时文件迁移，并删除临时文件
            if os.path.exists(self.path):
                with open(self.tmp_path, "rb") as fr:
                    with open(self.path, "wb") as fw:
                        fw.write(fr.read())
                os.remove(self.path)
            else:
                os.rename(self.tmp_path, self.path)
        self.switch_status()

        # 检查是否所有片段均已下载完成，如果是则合并
        if all([segment.done for segment in self.file.segments]):
            self.file.merge()
            self.file.switch_status()

    def remove(self):
        """ 删除文件及其临时文件 """
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)
        elif os.path.exists(self.path):
            os.remove(self.path)

    def switch_status(self, status=None):
        """ 切换到某一状态，默认为下一状态 """
        if status is None:
            self._status <<= 1
        else:
            self._status = status

    def get_size(self):
        """ 通过 os.path.getsize 获取片段大小 """
        try:
            if os.path.exists(self.tmp_path):
                size = os.path.getsize(self.tmp_path)
            elif os.path.exists(self.path):
                size = os.path.getsize(self.path)
            else:
                size = 0
        except FileNotFoundError:
            size = 0
        return size

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


class FileManager():
    """ 文件管理器

    负责资源的分发与文件监控

    属性
        files: 待管理文件 List
        pool: 线程池
        override: 是否强制覆盖，默认不强制覆盖
        spider: 爬虫会话，requests.Session() 的封装
        segment_size: 片段大小，单位为字节
    """

    def __init__(self, num_thread, segment_size, override=False, spider=Crawler()):
        self.files = []
        self.pool = ThreadPool(num_thread)
        self.override = override
        self.spider = spider
        self.segment_size = segment_size

    def dispense_resources(self, resources, log=True):
        """ 资源分发，将资源切分为片段，并分发至线程池 """

        for i, (url, file_path) in enumerate(resources):
            print("dispenser resources {}/{}".format(i, len(resources)), end="\r")
            file_name = os.path.split(file_path)[-1]
            if os.path.exists(file_path) and not self.override:
                if log:
                    print("------! {} already exist".format(file_name))
            else:
                if log:
                    print("------> {}".format(file_name))
                file = NetworkFile(url, file_path, segment_size=self.segment_size,
                                   override=self.override, spider=self.spider)
                for segment in file.segments:
                    task = Task(segment.download)
                    self.pool.add_task(task)
                self.files.append(file)

    def run(self):
        """ 启动任务 """
        self.pool.run()

    def monitoring(self):
        """ 启动监控器 """
        files = self.files
        size, t = sum([file.size for file in files]), time.time()
        total_size = sum([file.total for file in files])
        center_placeholder = "%(center)s"
        while len(files):
            bar_length = 50
            max_length = 80
            log_string = " Downloading... ".center(max_length, "=") + "\n"

            # 下载速度
            now_size, now_t = sum([file.size for file in files]), time.time()
            delta_size, delta_t = now_size - size, now_t - t
            size, t = now_size, now_t
            if delta_t < 1e-6:
                delta_t = 1e-6
            speed = delta_size / delta_t

            # 单个下载进度
            for file in files:
                if file.downloading:
                    num_segment_done = sum(
                        [segment.done for segment in file.segments])
                    num_segment = len(file.segments)
                    if file.total:
                        line = "{}({}/{}) {} {}/{}".format(file.name, num_segment_done, num_segment,
                                                         center_placeholder, size_format(file.size),
                                                         size_format(file.total))
                    else:
                        line = "{}({}/{}) {} {}".format(file.name, num_segment_done,
                                                      num_segment, center_placeholder, size_format(file.size))
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
                num_done = sum([file.done for file in files])
                num_total = len(files)
                len_done = bar_length * num_done // num_total
                len_undone = bar_length - len_done
                log_string += '{}{} {} {:12}'.format("#" * len_done, "_" * len_undone,
                                                     size_format(size), size_format(speed)+"/s")

            # 清空控制台并打印新的 log
            os.system('cls' if os.name == 'nt' else 'clear')
            print(log_string)

            # 监控是否全部完成
            if all([file.done for file in files]):
                break

            try:
                time.sleep(max(1-(time.time()-now_t), 0.01))
            except (SystemExit, KeyboardInterrupt):
                raise

        # 清空控制台
        os.system('cls' if os.name == 'nt' else 'clear')
