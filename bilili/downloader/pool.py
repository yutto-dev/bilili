import time
import queue
import threading


class Flag:
    def __init__(self, value=False):
        self.value = value

    def __bool__(self):
        return self.value

    def set(self):
        self.value = True

    def clear(self):
        self.value = False


class ThreadPool:
    """线程池类
    快速创建多个相同任务的线程池
    """

    def __init__(self, num, daemon=False, thread_globals_creator={}):
        self.num = num
        self.daemon = daemon
        self._taskQ = queue.Queue()
        self.threads = []
        self.__wait_flag = Flag(True)
        self.thread_globals_creator = thread_globals_creator

    def clear_flag(self):
        self.__wait_flag.clear()

    def set_flag(self):
        self.__wait_flag.set()

    def add_task(self, task):
        """ 添加任务　"""
        self._taskQ.put(task)

    def _run_task(self, **thread_globals):
        """ 启动任务线程　"""
        while True:
            if not self._taskQ.empty():
                task = self._taskQ.get(block=True, timeout=1)
                task(**thread_globals)
                self._taskQ.task_done()
            elif not self.__wait_flag:
                time.sleep(1)
            else:
                break

    def run(self):
        """ 启动线程池　"""
        for _ in range(self.num):
            thread_globals = {}
            for key, creator in self.thread_globals_creator.items():
                thread_globals[key] = creator()
            th = threading.Thread(target=self._run_task, kwargs={"thread_globals": thread_globals})
            th.setDaemon(self.daemon)
            self.threads.append(th)
            th.start()

    def join(self):
        """ 等待所有任务结束　"""
        for th in self.threads:
            th.join()


class RawExecutor:
    def __init__(self):
        pass

    def add_task(self, task):
        task()
