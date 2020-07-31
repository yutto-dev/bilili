import queue
import threading


class ThreadPool():
    """ 线程池类
    快速创建多个相同任务的线程池
    """
    def __init__(self, num):
        self.num = num
        self._taskQ = queue.Queue()
        self.threads = []

    def add_task(self, task):
        """ 添加任务　"""
        self._taskQ.put(task)

    def _run_task(self):
        """ 启动任务线程　"""
        while True:
            if not self._taskQ.empty():
                task = self._taskQ.get(block = True, timeout = 1)
                task()
                self._taskQ.task_done()
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
