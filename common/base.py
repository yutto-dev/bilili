import os
import re


class Task():
    """任务对象"""

    def __init__(self, func, args=(), kw={}):
        """接受函数与参数以初始化对象"""

        self.func = func
        self.args = args
        self.kw = kw

    def __call__(self):
        """执行函数
        同步函数直接执行并返回结果，异步函数返回该函数
        """

        result = self.func(*self.args, **self.kw)
        return result


class Writer():
    """ 文件写入器，持续打开文件对象，直到使用完毕后才关闭 """

    def __init__(self, path, mode='wb', **kw):
        self.path = path
        self._f = open(path, mode, **kw)

    def __del__(self):
        self._f.close()

    def flush(self):
        self._f.flush()

    def write(self, content):
        self._f.write(content)


class Text(Writer):
    """ 文本写入器 """

    def __init__(self, path, **kw):
        kw['encoding'] = kw.get('encoding', 'utf-8')
        super().__init__(path, 'w', **kw)

    def write_string(self, string):
        self.write(string + '\n')


def touch_dir(path):
    """ 若文件夹不存在则新建，并返回标准路径 """
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.normpath(path)


def touch_file(path):
    """ 若文件不存在则新建，并返回标准路径 """
    if not os.path.exists(path):
        open(path, 'w').close()
    return os.path.normpath(path)


def repair_filename(filename):
    """ 修复不合法的文件名 """
    regex_path = re.compile(r'[\\/:*?"<>|]')
    return regex_path.sub('', filename)


def get_size(path):
    """ 获取文件夹或文件的字节数 """
    if os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        size = 0
        for subpath in os.listdir(path):
            size += get_size(os.path.join(path, subpath))
        return size
    else:
        return 0


def size_format(size, ndigits=2):
    """ 输入数据字节数，与保留小数位数，返回数据量字符串 """
    flag = '-' if size < 0 else ''
    size = abs(size)
    units = ["Bytes", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "BB"]
    idx = len(units) - 1
    unit = ""
    unit_size = 0
    while idx >= 0:
        unit_size = 2 ** (idx * 10)
        if size >= unit_size:
            unit = units[idx]
            break
        idx -= 1
    return "{}{:.{}f} {}".format(flag, size/unit_size, ndigits, unit)


def get_string_width(string):
    """ 计算包含中文的字符串宽度 """
    try:
        length = len(string.encode('gbk'))
    except:
        length = len(string)
    return length
