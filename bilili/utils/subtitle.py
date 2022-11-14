from ..utils.base import Text


class Subtitle(Text):
    """播放列表类"""

    def __init__(self, path: str):
        super().__init__(path)
        self._count = 0

    @staticmethod
    def time_format(seconds: int):
        ms = int(1000 * (seconds - int(seconds)))
        seconds = int(seconds)
        minutes, sec = seconds // 60, seconds % 60
        hour, min = minutes // 60, minutes % 60
        return "{:02}:{:02}:{:02},{}".format(hour, min, sec, ms)

    def write_line(self, content: str, from_time: int, to_time: int) -> None:
        self._count += 1
        self.write_string(str(self._count))
        self.write_string("{} --> {}".format(self.time_format(from_time), self.time_format(to_time)))
        self.write_string(content + "\n")
