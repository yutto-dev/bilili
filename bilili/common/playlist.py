import os

from bilili.common.base import Text


class Playlist(Text):
    """ 播放列表类 """

    def __init__(self, path, path_type):
        super().__init__(path)
        self.path_type = path_type

    def switch_path(self, path):
        path = os.path.normpath(path)
        if self.path_type == 'AP':
            path = os.path.abspath(path)
        elif self.path_type == 'RP':
            path = os.path.relpath(path, start=os.path.dirname(self.path))
        return path

    def write_path(self, path):
        path = self.switch_path(path)
        self.write_string(path)


class M3u(Playlist):
    """ m3u 播放列表 """

    def __init__(self, path, path_type='RP'):
        super().__init__(path, path_type)


class Dpl(Playlist):
    """ potplayer 播放列表 """

    def __init__(self, path, path_type='RP'):
        super().__init__(path, path_type)
        self.write_string('DAUMPLAYLIST\n')
        self._count = 0

    def write_path(self, path, name=None):
        self._count += 1
        path = self.switch_path(path)
        self.write_string('{}*file*{}'.format(self._count, path))
        if name is not None:
            self.write_string('{}*title*{}\n'.format(self._count, name))
