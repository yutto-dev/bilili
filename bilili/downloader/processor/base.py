from typing import Enum

noop = lambda *args, **kwargs: None


class Status(Enum):
    TODO = 0
    IN_PROGRESS = 1
    DONE = 2


class Task:
    """ 任务对象 """

    def __init__(self, func, args=(), kwargs={}):
        """ 接受函数与参数以初始化对象 """

        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, **extra_params):
        """ 执行函数 """

        result = self.func(*self.args, **self.kwargs, **extra_params)
        return result


class Processor(Task):
    def __init__(self, args=(), kwargs={}):
        super().__init__(self.__run, args, kwargs)
        self.__status = Status.TODO
        self.next = noop
        self.file = None

    def bind(self, file):
        self.file = file

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __run(self, *args, **kwargs):
        self.in_progress = True
        self.run(*args, **kwargs)
        self.done = True
        self.next.bind(self.file)
        self.next(**kwargs)

    def to(self, pool):
        pool.add_task(self)

    def then(self, process):
        self.next = process

    @property
    def todo(self):
        return self.__status == Status.TODO

    @todo.setter
    def todo(self, value):
        if value:
            self.__status = Status.TODO
        else:
            print("[WARNING] 无法设置为 False")

    @property
    def in_progress(self):
        return self.__status == Status.IN_PROGRESS

    @in_progress.setter
    def in_progress(self, value):
        if value:
            self.__status = Status.IN_PROGRESS
        else:
            print("[WARNING] 无法设置为 False")

    @property
    def done(self):
        return self.__status == Status.DONE

    @done.setter
    def done(self, value):
        if value:
            self.__status = Status.DONE
            if self.file is not None:
                for child in self.file.children:
                    child.processor.done = True
        else:
            print("[WARNING] 无法设置为 False")
