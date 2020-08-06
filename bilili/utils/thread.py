import time
import queue
import threading


from bilili.utils.base import Ref


class Flag(Ref):

    def __init__(self, value=False):
        super().__init__(value)


class Task():
    """ 任务对象 """

    def __init__(self, func, args=(), kwargs={}):
        """ 接受函数与参数以初始化对象 """

        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        """执行函数

        同步函数直接执行并返回结果
        """

        result = self.func(*self.args, **self.kwargs)
        return result


class ThreadPool():
    """ 线程池类
    快速创建多个相同任务的线程池
    """

    def __init__(self, num, wait=Flag(True)):
        self.num = num
        self._taskQ = queue.Queue()
        self.threads = []
        self.__wait_flag = wait

    def add_task(self, func, args=(), kwargs={}):
        """ 添加任务　"""
        self._taskQ.put(Task(func, args, kwargs))

    def _run_task(self):
        """ 启动任务线程　"""
        while True:
            if not self._taskQ.empty():
                task = self._taskQ.get(block=True, timeout=1)
                task()
                self._taskQ.task_done()
            elif not self.__wait_flag.value:
                time.sleep(1)
            else:
                break

    def run(self):
        """ 启动线程池　"""
        for _ in range(self.num):
            th = threading.Thread(target=self._run_task)
            th.setDaemon(True)
            self.threads.append(th)
            th.start()

    def join(self):
        """ 等待所有任务结束　"""
        self._taskQ.join()
