import os
import requests

from bilili.utils.base import touch_dir, touch_file


class ASS():
    plugin_url = "https://raw.githubusercontent.com/m13253/danmaku2ass/master/danmaku2ass.py"
    plugin_path = "plugins/danmaku2ass.py"
    def __init__(self):
        self.has_plugin = os.path.exists(ASS.plugin_path)

    def initial_plugin(self):
        if self.has_plugin:
            return
        touch_dir(os.path.dirname(ASS.plugin_path))
        touch_file(os.path.join(os.path.dirname(ASS.plugin_path), "__init__.py"))
        print("下载弹幕转换插件中……")
        res = requests.get(ASS.plugin_url)
        with open(ASS.plugin_path, "w", encoding="utf8") as f:
            f.write(res.text)
        self.has_plugin = True

    def convert_danmaku_from_xml(self, xml_path, height, width):
        self.initial_plugin()
        from plugins.danmaku2ass import Danmaku2ASS
        ass_path = os.path.splitext(xml_path)[0] + '.ass'
        if not os.path.exists(xml_path):
            return
        Danmaku2ASS(
            xml_path, "autodetect", ass_path,
            width, height, reserve_blank=0,
            font_face=_('(FONT) sans-serif')[7:],
            font_size=width/40, text_opacity=0.8, duration_marquee=15.0,
            duration_still=10.0, comment_filter=None, is_reduce_comments=False,
            progress_callback=None)
        os.remove(xml_path)
