import math
import os
import platform
import shutil
import sys
from typing import Any, List, Optional, Tuple, Union

from ..base import get_string_width
from .colorful import Back, Fore, Style, colored_string
from .logger import Logger

IS_WINDOWS = platform.system() == "Windows"


def get_terminal_size() -> Tuple[int, int]:
    """Get the size of the console.
    @refs: https://github.com/willmcgugan/rich/blob/e5246436cd75de32f3436cc88d6e4fdebe13bd8d/rich/console.py#L918-L951
    Returns:
        tuple[int, int]: A named tuple containing the dimensions.
    """

    width: Optional[int] = None
    height: Optional[int] = None
    if IS_WINDOWS:  # pragma: no cover
        width, height = shutil.get_terminal_size()
    else:
        try:
            width, height = os.get_terminal_size(sys.stdin.fileno())
        except (AttributeError, ValueError, OSError):
            try:
                width, height = os.get_terminal_size(sys.stdout.fileno())
            except (AttributeError, ValueError, OSError):
                pass

    width = width or 80
    height = height or 25
    return (width, height)


class View:
    max_width = 100
    min_width = 50

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.components = []
        self.rendered_area = (0, 0)

    def add_component(self, component: "Component"):
        self.components.append(component)

    def render(self, data: Any) -> str:
        if data is None:
            return ""
        assert len(self.components) == len(data), "数据个数与组件个数不匹配"
        result = ""
        for component, component_data in zip(self.components, data):
            result += component.render(component_data)
        self.rendered_area = View.calc_area_size(result)
        return result

    def refresh(self, data: Any):
        if not self.debug:
            self.clear()
        Logger.print(self.render(data))

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")
        # 暂时无法判断什么终端支持什么终端不支持（如 cmd），暂时不使用
        # if self.rendered_area == (0, 0):
        #     return
        # clear_str = ""
        # clear_str += "\x1b[1A" * self.rendered_area[0]
        # clear_str += "\r"
        # # 这里不应该使用 Logger 打印，因为可能被去除颜色控制符（虽然现在不会）
        # print(clear_str, end="")

    @classmethod
    def get_width(cls) -> int:
        width = get_terminal_size()[0]
        width = min(width, View.max_width)
        width = max(width, View.min_width)
        return width

    @classmethod
    def get_height(cls) -> int:
        return get_terminal_size()[1]

    @classmethod
    def calc_area_size(cls, string: str) -> Tuple[int, int]:
        lines = string.split("\n")
        return (len(lines), get_string_width(lines[0]))


class Component:
    def __init__(self):
        pass

    def render(self, data: Any) -> str:
        raise NotImplementedError


class String(Component):
    def __init__(self):
        super().__init__()

    def render(self, data: Any) -> str:
        if data is None:
            return ""
        return data


class EndLine(Component):
    def __init__(self):
        super().__init__()

    def render(self, data: Any) -> str:
        if data is None:
            return ""
        return "\n"


class Font(Component):
    def __init__(self, char_a: str = "ａ", char_A: Optional[str] = None):
        super().__init__()
        self.char_a = char_a
        self.char_A = char_A

    def render(self, data: Any) -> str:
        if data is None:
            return ""
        result = ""
        for char in data:
            if ord(char) >= ord("a") and ord(char) <= ord("z"):
                result += chr(ord(char) + ord(self.char_a) - ord("a"))
            elif ord(char) >= ord("A") and ord(char) <= ord("Z"):
                if self.char_A is None:
                    result += chr(ord(char) + ord(self.char_a) - ord("a"))
                else:
                    result += chr(ord(char) + ord(self.char_A) - ord("A"))
            else:
                result += char
        return result


class ColorString(Component):
    def __init__(
        self,
        fore: Optional[Fore] = None,
        back: Optional[Back] = None,
        style: Optional[Style] = None,
        subcomponent: Optional[Component] = None,
    ):
        super().__init__()
        self.fore: Optional[Fore] = fore
        self.back: Optional[Back] = back
        self.style: Optional[Style] = style
        self.subcomponent: Optional[Component] = subcomponent

    def render(self, data: Any) -> str:
        if data is None:
            return ""
        subcomponet_string = self.subcomponent.render(data) if self.subcomponent is not None else data
        return colored_string(subcomponet_string, self.fore, self.back, self.style)


class Line(Component):
    def __init__(
        self,
        left: Optional[Component] = None,
        center: Optional[Component] = None,
        right: Optional[Component] = None,
        fillchar: str = " ",
    ):
        super().__init__()
        self.left = left
        self.center = center
        self.right = right
        self.fillchar = fillchar

    def render(self, data: Any) -> str:
        if data is None:
            return ""
        left_data = data.get("left", None)
        center_data = data.get("center", None)
        right_data = data.get("right", None)

        left_result, center_result, right_result = "", "", ""
        left_width, center_width, right_width = 0, 0, 0
        left_placeholder_width, right_placeholder_width = 0, 0
        if self.left is not None:
            assert left_data is not None
            left_result = self.left.render(left_data)
            left_width: int = get_string_width(left_result)
        if self.right is not None:
            assert right_data is not None
            right_result = self.right.render(right_data)
            right_width: int = get_string_width(right_result)
        if self.center is not None:
            assert center_data is not None
            center_result = self.center.render(center_data)
            center_width: int = get_string_width(center_result)

        if self.center is not None:
            left_placeholder_width = (View.get_width() - center_width) // 2 - left_width
            right_placeholder_width = (
                View.get_width() - left_width - left_placeholder_width - center_width - right_width
            )

            return (
                left_result
                + left_placeholder_width * self.fillchar
                + center_result
                + right_placeholder_width * self.fillchar
                + right_result
                + "\n"
            )
        else:
            left_placeholder_width = View.get_width() - left_width - right_width
            return left_result + left_placeholder_width * self.fillchar + right_result + "\n"


class Center(Component):
    def __init__(self, fillchar: str = " "):
        super().__init__()
        self.fillchar = fillchar

    def render(self, data: Any) -> str:
        if data is None:
            return ""
        return data.center(View.get_width(), self.fillchar) + "\n"


class ProgressBar(Component):
    def __init__(self, symbols: Union[str, List[str]] = "░▏▎▍▌▋▊▉█", width: int = View.get_width()):
        super().__init__()
        self.width = width
        self.symbols = symbols
        assert len(symbols) >= 2, "symbols 至少为 2 个"
        self.num_symbol = len(symbols)

    def render(self, data: Any) -> str:
        if data is None:
            return ""
        if data == 1:
            return self.symbols[-1] * self.width
        length = self.width * data
        length_int = int(length)
        length_float = length - length_int

        return (
            length_int * self.symbols[-1]
            + self.symbols[math.floor(length_float * (self.num_symbol - 1))]
            + (self.width - length_int - 1) * self.symbols[0]
        )


class DynamicSymbol(Component):
    def __init__(self, symbols: Union[str, List[str]] = "⠁⠂⠄⡀⢀⠠⠐⠈"):
        super().__init__()
        self.symbols = symbols
        self.index = 0

    def render(self, data: Any) -> str:
        if data is None:
            return ""
        self.index += 1
        self.index %= len(self.symbols)
        return self.symbols[self.index]


class LineList(Component):
    def __init__(self, subcomponent: Component):
        super().__init__()
        self.subcomponent = subcomponent

    def render(self, data: Any) -> str:
        if data is None:
            return ""
        result = ""
        for item in data:
            result += self.subcomponent.render(item)
        return result


if __name__ == "__main__":
    import time

    console = View()
    console.add_component(Line(center=Font(char_a="𝓪", char_A="𝓐"), fillchar="="))
    console.add_component(Line(left=ColorString(fore="cyan", style="italic"), fillchar=" "))
    console.add_component(LineList(Line(left=String(), right=String(), fillchar="-")))
    console.add_component(Line(left=ColorString(fore="blue", style="italic"), fillchar=" "))
    console.add_component(LineList(Line(left=String(), right=String(), fillchar="-")))
    console.add_component(
        Line(
            left=ColorString(
                fore="green",
                back="white",
                subcomponent=ProgressBar(symbols=" ▏▎▍▌▋▊▉█", width=70),
            ),
            right=String(),
            fillchar=" ",
        )
    )
    for i in range(100):
        console.refresh([
            {
                'center': ' 🍻 bilili ',
            },
            {
                'left': '🌠 Downloading videos:'
            },
            [
                {'left': '视频 1 ', 'right': ' 50%'},
                {'left': '视频 2 ', 'right': ' 40%'}
            ],
            {
                'left': '🍰 Merging videos:'
            },
            [
                {'left': '视频 3 ', 'right': ' 50%'},
                {'left': '视频 4 ', 'right': ' 40%'}
            ],
            {
                'left': (i+1) / 100,
                'right': "100MB/123MB 11.2 MB/s ⚡"
            }
        ])  # fmt: skip
        time.sleep(0.01)
