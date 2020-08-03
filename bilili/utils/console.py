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
        assert len(self.components) == len(data)
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

    def __init__(self, undone_char='_', done_char='#', width=Console.max_width):
        super().__init__()
        self.width = width
        self.undone_char = undone_char
        self.done_char = done_char

    def render(self, data):
        if data is None:
            return ''
        num_done = math.ceil(self.width * data)
        num_undone = self.width - num_done

        return num_done * self.done_char + num_undone * self.undone_char


class DynamicSign(Component):

    def __init__(self, charset='⠁⠂⠄⡀⢀⠠⠐⠈'):
        super().__init__()
        self.charset = charset
        self.index = 0

    def render(self, data):
        if data is None:
            return ''
        self.index += 1
        self.index %= len(self.charset)
        return self.charset[self.index]


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
    console.add_component(Line(left=String(), fillchar=' '))
    console.add_component(
        List(Line(left=String(), right=String(), fillchar='-')))
    console.add_component(Line(left=String(), fillchar=' '))
    console.add_component(
        List(Line(left=String(), right=String(), fillchar='-')))
    console.add_component(Line(left=ProgressBar(
        width=70), right=String(), fillchar=' '))
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
        time.sleep(1)
