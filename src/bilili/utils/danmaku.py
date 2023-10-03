from biliass import Danmaku2ASS


def convert_xml_danmaku_to_ass(xml_text: str, height: int, width: int) -> str:
    return Danmaku2ASS(
        xml_text,
        width,
        height,
        input_format="xml",
        reserve_blank=0,
        font_face="sans-serif",
        font_size=width / 40,
        text_opacity=0.8,
        duration_marquee=15.0,
        duration_still=10.0,
        comment_filter=None,
        is_reduce_comments=False,
        progress_callback=None,
    )
