import os


class ASS:
    def __init__(self):
        pass

    def convert_danmaku_from_xml(self, xml_path: str, height: int, width: int):
        from ..plugins.danmaku2ass import Danmaku2ASS

        ass_path = os.path.splitext(xml_path)[0] + ".ass"
        if not os.path.exists(xml_path):
            return
        Danmaku2ASS(
            xml_path,
            "autodetect",
            ass_path,
            width,
            height,
            reserve_blank=0,
            font_face=_("(FONT) sans-serif")[7:],
            font_size=width / 40,
            text_opacity=0.8,
            duration_marquee=15.0,
            duration_still=10.0,
            comment_filter=None,
            is_reduce_comments=False,
            progress_callback=None,
        )
        os.remove(xml_path)
