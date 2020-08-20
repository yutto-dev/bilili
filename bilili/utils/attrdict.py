from itertools import chain


class AttrDict(dict):
    """ AttrDict 类
    像 JS 的 Object 一样方便地读写键值对
    继承于 dict，也可直接使用属性进行读写，避免大量使用字符串的繁琐行为

    将 dict 转化为 AttrDict 的方法：
    ```
    >>> ad = AttrDict({'key': 'value'})
    >>> ad = {'key': 'value'} >> AttrDict()
    ```
    """

    def __init__(self, iterable=None, **kwargs):
        if iterable is not None:
            self.__init(iterable, **kwargs)

    def __init(self, iterable, **kwargs):
        """ 通过 dict 初始化 """
        super().__init__(iterable, **kwargs)
        for key, value in chain(self.items(), kwargs.items()):
            if isinstance(value, dict):
                self[key] = AttrDict(value)

    def __getattr__(self, key):
        """ 将属性的 get 重定向到 dict 的 get """
        try:
            return self[key]
        except KeyError:
            raise AttributeError(
                r"'AttrDict' object has no attribute '{}'".format(key))

    def __setattr__(self, key, value):
        """ 将属性的 set 重定向到 dict 的 set """
        self[key] = value

    def __delattr__(self, key):
        """ 将属性的 del 重定向到 dict 的 del """
        del self[key]

    def __setitem__(self, key, value):
        """ 确保当新的 value 为 dict 时需要将其转为 AttrDict """
        if isinstance(value, dict):
            super().__setitem__(key, AttrDict(value))
        else:
            super().__setitem__(key, value)

    def __rrshift__(self, d):
        """ 添加 >> 快速转换方法 """
        self.__init(d)
        return self
