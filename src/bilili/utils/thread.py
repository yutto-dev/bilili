import queue
import threading
import time

from ..utils.base import Ref


class Flag(Ref):
    def __init__(self, value=False):
        super().__init__(value)


class Task:
    """任务对象"""

    def __init__(self, func, args=(), kwargs={}):
        """接受函数与参数以初始化对象"""

        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, **extra_params):
        """执行函数

        同步函数直接执行并返回结果
        """

        result = self.func(*self.args, **self.kwargs, **extra_params)
        return result


class ThreadPool:
    """线程池类
    快速创建多个相同任务的线程池
    """

    def __init__(self, num, wait=Flag(True), daemon=False, thread_globals_creator={}):
        self.num = num
        self.daemon = daemon
        self._taskQ = queue.Queue()
        self.threads = []
        self.__wait_flag = wait
        self.thread_globals_creator = thread_globals_creator

    def add_task(self, func, args=(), kwargs={}):
        """添加任务"""
        self._taskQ.put(Task(func, args, kwargs))

    def _run_task(self, **thread_globals):
        """启动任务线程"""
        while True:
            if not self._taskQ.empty():
                task = self._taskQ.get(block=True, timeout=1)
                task(**thread_globals)
                self._taskQ.task_done()
            elif not self.__wait_flag.value:
                time.sleep(1)
            else:
                break

    def run(self):
        """启动线程池"""
        for _ in range(self.num):
            thread_globals = {}
            for key, creator in self.thread_globals_creator.items():
                thread_globals[key] = creator()
            th = threading.Thread(target=self._run_task, kwargs=thread_globals)
            th.setDaemon(self.daemon)
            self.threads.append(th)
            th.start()

    def join(self):
        """等待所有任务结束"""
        for th in self.threads:
            th.join()
