import os
import re
import unicodedata


class Ref():
    """ 引用类

    用于包裹基本数据类型，将其封装为对象，其值通过 var.value 来访问
    """
    def __init__(self, value):
        self.value = value


class Writer():
    """ 文件写入器，持续打开文件对象，直到使用完毕后才关闭 """

    def __init__(self, path, mode='wb', **kwargs):
        self.path = path
        self._f = open(path, mode, **kwargs)

    def __del__(self):
        self._f.close()

    def flush(self):
        self._f.flush()

    def write(self, content):
        self._f.write(content)


class Text(Writer):
    """ 文本写入器 """

    def __init__(self, path, **kwargs):
        kwargs['encoding'] = kwargs.get('encoding', 'utf-8')
        super().__init__(path, 'w', **kwargs)

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


def touch_url(url, spider):
    """ 与资源进行测试连接，并获取该资源的 size 与 是否可以断点续传 """
    res = spider.head(url, headers={'Range': 'bytes=0-4'})
    size, resumable = None, False
    if res.headers.get('Content-Range'):
        size = int(res.headers['Content-Range'].split('/')[-1])
        resumable = True
    elif res.headers.get('Content-Length'):
        size = int(res.headers['Content-Length'])
        resumable = False
    else:
        size = None
        resumable = False
    return size, resumable


def repair_filename(filename):
    """ 修复不合法的文件名 """
    def to_full_width_chr(matchobj):
        char = matchobj.group(0)
        full_width_char = chr(ord(char) + ord('？') - ord('?'))
        return full_width_char
    # 路径非法字符，转全角
    regex_path = re.compile(r'[\\/:*?"<>|]')
    # 空格类字符，转空格
    regex_spaces = re.compile(r'\s+')
    # 不可打印字符，移除
    regex_non_printable = re.compile(
        r'[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        r'\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]')

    filename = regex_path.sub(to_full_width_chr, filename)
    filename = regex_spaces.sub(' ', filename)
    filename = regex_non_printable.sub('', filename)
    filename = filename.strip()
    return filename


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


def get_char_width(char):
    """ 计算单个字符的宽度 """
    widths = [
        (126,    1), (159,    0), (687,     1), (710,   0), (711,   1),
        (727,    0), (733,    1), (879,     0), (1154,  1), (1161,  0),
        (4347,   1), (4447,   2), (7467,    1), (7521,  0), (8369,  1),
        (8426,   0), (9000,   1), (9002,    2), (11021, 1), (12350, 2),
        (12351,  1), (12438,  2), (12442,   0), (19893, 2), (19967, 1),
        (55203,  2), (63743,  1), (64106,   2), (65039, 1), (65059, 0),
        (65131,  2), (65279,  1), (65376,   2), (65500, 1), (65510, 2),
        (120831, 1), (262141, 2), (1114109, 1),
    ]

    o = ord(char)
    if o == 0xe or o == 0xf:
        return 0
    for num, wid in widths:
        if o <= num:
            return wid
    return 1


def get_string_width(string):
    """ 计算包含中文的字符串宽度 """
    # 去除颜色码
    regex_color = re.compile(r'\033\[\d+m')
    string = regex_color.sub('', string)
    try:
        length = sum([get_char_width(c) for c in string])
    except:
        length = len(string)
    return length
