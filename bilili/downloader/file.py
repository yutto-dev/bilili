import os

from bilili.downloader.processor.base import Processor, noop


class Tree:
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

    @property
    def leaves(self):
        if self.is_leaf:
            return [self]
        leaves = []
        for child in self.children:
            leaves.extend(child.leaves)
        return leaves


class CombinedFile(Tree):
    def __init__(self, path, processor, pool):
        super().__init__(parent=None, children=[])
        self.path = path
        self.processor = processor
        self.pool = pool

        # status
        self.__total_size = 0
        self.__size = 0

    def process(self):
        self.processor.then(PostProcessor())
        self.processor.to(self.pool)

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
            print("[WARNING] 无法设定非叶子结点的 total_size")

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
            print("[WARNING] 无法设定非叶子结点的 size")

    def check_status(self, overwrite=False):
        if overwrite:
            if os.path.exists(self.path):
                os.remove(self.path)
            if os.path.exists(self.path + ".dl"):
                os.remove(self.path + ".dl")
            return True
        if os.path.exists(self.path):
            return False
        return True


class PostProcessor(Processor):
    def run(self, *args, **kwargs):
        assert self.file is not None
        if all([child.done for child in self.file.parent.children]):
            self.file.parent.process()
