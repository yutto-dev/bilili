import os
import math

from bilili.utils.base import get_string_width


class Console():
    max_width = 100

    def __init__(self, debug=False):
        self.debug = debug
        self.components = []

    def add_component(self, component):
        self.components.append(component)

    def render(self, data):
        if data is None:
            return ''
        assert len(self.components) == len(data), '数据个数与组件个数不匹配'
        result = ''
        for component, component_data in zip(self.components, data):
            result += component.render(component_data)
        return result

    def refresh(self, data):
        if not self.debug:
            self.clear()
        print(self.render(data))

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')


class Component():

    def __init__(self):
        pass

    def render(self, data):
        raise NotImplementedError


class String(Component):

    def __init__(self):
        super().__init__()

    def render(self, data):
        if data is None:
            return ''
        return data


class EndLine(Component):

    def __init__(self):
        super().__init__()

    def render(self, data):
        if data is None:
            return ''
        return '\n'


class Font(Component):

    def __init__(self, char_a='ａ', char_A=None):
        super().__init__()
        self.char_a = char_a
        self.char_A = char_A

    def render(self, data):
        if data is None:
            return ''
        result = ''
        for char in data:
            if (ord(char) >= ord('a') and ord(char) <= ord('z')):
                result += chr(ord(char) + ord(self.char_a) - ord('a'))
            elif (ord(char) >= ord('A') and ord(char) <= ord('Z')):
                if self.char_A is None:
                    result += chr(ord(char) + ord(self.char_a) - ord('a'))
                else:
                    result += chr(ord(char) + ord(self.char_A) - ord('A'))
            else:
                result += char
        return result


class ColorString(Component):

    code_map = {
        'fore': {
            'black': 30,
            'red': 31,
            'green': 32,
            'yellow': 33,
            'blue': 34,
            'magenta': 35,
            'cyan': 36,
            'white': 37,
        },
        'back': {
            'black': 40,
            'red': 41,
            'green': 42,
            'yellow': 43,
            'blue': 44,
            'magenta': 45,
            'cyan': 46,
            'white': 47,
        },
        'style': {
            'reset': 0,
            'bold': 1,
            'italic': 3,
            'underline': 4,
            'defaultfg': 39,
            'defaultbg': 49,
        }
    }

    template = '\033[{code}m'

    def __init__(self, fore=None, back=None, style=None, subcomponent=None):
        super().__init__()
        self.fore = fore
        self.back = back
        self.style = style
        self.subcomponent = subcomponent

    def render(self, data):
        if data is None:
            return ''
        result = ''
        if self.fore is not None:
            result += ColorString.template.format(code=ColorString.code_map['fore'][self.fore])
        if self.back is not None:
            result += ColorString.template.format(code=ColorString.code_map['back'][self.back])
        if self.style is not None:
            result += ColorString.template.format(code=ColorString.code_map['style'][self.style])
        result += self.subcomponent.render(data) if self.subcomponent is not None else data
        result += ColorString.template.format(code=ColorString.code_map['style']['reset'])
        return result


class Line(Component):

    def __init__(self, left=None, center=None, right=None, fillchar=' '):
        super().__init__()
        self.left = left
        self.center = center
        self.right = right
        self.fillchar = fillchar

    def render(self, data):
        if data is None:
            return ''
        left_data = data.get('left', None)
        center_data = data.get('center', None)
        right_data = data.get('right', None)

        left_result, center_result, right_result = '', '', ''
        left_width, center_width, right_width = 0, 0, 0
        left_placeholder_width, right_placeholder_width = 0, 0
        if self.left is not None:
            assert left_data is not None
            left_result = self.left.render(left_data)
            left_width = get_string_width(left_result)
        if self.right is not None:
            assert right_data is not None
            right_result = self.right.render(right_data)
            right_width = get_string_width(right_result)
        if self.center is not None:
            assert center_data is not None
            center_result = self.center.render(center_data)
            center_width = get_string_width(center_result)

        if self.center is not None:
            left_placeholder_width = (
                Console.max_width - center_width) // 2 - left_width
            right_placeholder_width = Console.max_width - left_width - \
                left_placeholder_width - center_width - right_width

            return left_result + left_placeholder_width * self.fillchar + \
                center_result + right_placeholder_width * self.fillchar + right_result + '\n'
        else:
            left_placeholder_width = Console.max_width - left_width - right_width
            return left_result + left_placeholder_width * self.fillchar + right_result + '\n'


class Center(Component):

    def __init__(self, fillchar=' '):
        super().__init__()
        self.fillchar = fillchar

    def render(self, data):
        if data is None:
            return ''
        return data.center(Console.max_width, self.fillchar) + '\n'


class ProgressBar(Component):

    def __init__(self, symbols='░▏▎▍▌▋▊▉█', width=Console.max_width):
        super().__init__()
        self.width = width
        self.symbols = symbols
        assert len(symbols) >= 2, "symbols 至少为 2 个"
        self.num_symbol = len(symbols)

    def render(self, data):
        if data is None:
            return ''
        if data == 1:
            return self.symbols[-1] * self.width
        length = self.width * data
        length_int = int(length)
        length_float = length - length_int

        return length_int * self.symbols[-1] + \
                self.symbols[math.floor(length_float * (self.num_symbol-1))] + \
                (self.width - length_int - 1) * self.symbols[0]


class DynamicSymbol(Component):

    def __init__(self, symbols='⠁⠂⠄⡀⢀⠠⠐⠈'):
        super().__init__()
        self.symbols = symbols
        self.index = 0

    def render(self, data):
        if data is None:
            return ''
        self.index += 1
        self.index %= len(self.symbols)
        return self.symbols[self.index]


class List(Component):

    def __init__(self, subcomponent):
        super().__init__()
        self.subcomponent = subcomponent

    def render(self, data):
        if data is None:
            return ''
        result = ''
        for item in data:
            result += self.subcomponent.render(item)
        return result


if __name__ == '__main__':
    import time
    console = Console()
    console.add_component(
        Line(center=Font(char_a='𝓪', char_A='𝓐'), fillchar='='))
    console.add_component(Line(left=ColorString(fore='cyan', style='italic'), fillchar=' '))
    console.add_component(
        List(Line(left=String(), right=String(), fillchar='-')))
    console.add_component(Line(left=ColorString(fore='blue', style='italic'), fillchar=' '))
    console.add_component(
        List(Line(left=String(), right=String(), fillchar='-')))
    console.add_component(Line(left=ColorString(fore='green', back='white', subcomponent=ProgressBar(
        symbols=' ▏▎▍▌▋▊▉█', width=70)), right=String(), fillchar=' '))
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
        ])
        time.sleep(0.1)
