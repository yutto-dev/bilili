class Middleware():
    """ 多层次中间件类 """
    def __init__(self, parent=None, children=[]):
        self.parent = None
        self.children = []
        if parent is not None:
            self.set_parent(parent)
        if children:
            self.add_children(children)

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def set_parent(self, parent):
        parent.add_child(self)

    def add_children(self, children):
        for child in children:
            self.add_child(child)

    @property
    def is_leaf(self):
        return not self.children

    @property
    def is_root(self):
        return self.parent is None

class DownloaderMiddleware(Middleware):
    """ 下载中间件类

    用于下载器与外部程序之间的通讯
    """

    def __init__(self, parent=None, children=[]):
        super().__init__(parent=parent, children=children)
        self.__total_size = 0
        self.__size = 0
        self.__downloading = False
        self.__downloaded = False
        self.__merging = False
        self.__merged = False

    @property
    def total_size(self):
        if self.is_leaf:
            return self.__total_size
        else:
            return sum([child.total_size for child in self.children])

    @total_size.setter
    def total_size(self, value):
        if self.is_leaf:
            self.__total_size = value
        else:
            print("[warn] 无法设定非叶子结点的 total_size")

    @property
    def size(self):
        if self.is_leaf:
            if self.downloaded:
                return self.total_size
            return self.__size
        else:
            return sum([child.size for child in self.children])

    @size.setter
    def size(self, value):
        if self.is_leaf:
            self.__size = value
        else:
            print("[warn] 无法设定非叶子结点的 size")

    @property
    def downloading(self):
        if self.is_leaf:
            return self.__downloading
        else:
            return any([child.downloading for child in self.children])

    @downloading.setter
    def downloading(self, value):
        if self.is_leaf:
            self.__downloading = value
        else:
            if value:
                print("[warn] 无法设定非叶子结点的 downloading 为 True")
            else:
                for child in self.children:
                    child.downloading = False

    @property
    def downloaded(self):
        if self.is_leaf:
            return self.__downloaded
        else:
            return all([child.downloaded for child in self.children])

    @downloaded.setter
    def downloaded(self, value):
        if self.is_leaf:
            self.__downloaded = value
        else:
            if value:
                for child in self.children:
                    child.downloaded = True
            else:
                print("[warn] 无法设定非叶子结点的 downloaded 为 False")

    @property
    def merging(self):
        if self.is_leaf:
            return self.__merging
        else:
            return any([child.merging for child in self.children])

    @merging.setter
    def merging(self, value):
        if self.is_leaf:
            self.__merging = value
        else:
            if value:
                # 由于合并是共同进行的，所以可以由父结点来设置
                for child in self.children:
                    child.merging = True
            else:
                for child in self.children:
                    child.merging = False

    @property
    def merged(self):
        if self.is_leaf:
            return self.__merged
        else:
            return all([child.merged for child in self.children])

    @merged.setter
    def merged(self, value):
        if self.is_leaf:
            self.__merged = value
        else:
            if value:
                for child in self.children:
                    child.merged = True
            else:
                print("[warn] 无法设定非叶子结点的 merged 为 False")
