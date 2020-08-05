import pytest

from bilili.api.acg_video import get_title, get_context, get_containers, parse_segments
from bilili.utils.base import touch_dir
from bilili.utils.quality import quality_sequence_default
from bilili.video import BililiContainer


def test_get_title():
    url = "https://www.bilibili.com/video/BV1Y441167U2/"
    assert get_title(url) == "慕课课程下载工具 Course Crawler 使用方法简介"

def test_get_context():
    url = "https://www.bilibili.com/video/BV1Y441167U2/"
    context = get_context(url)
    assert context["avid"] == ''
    assert context["bvid"] == '1Y441167U2'

def test_get_containers():
    context = {
        "avid": '',
        "bvid": '1Y441167U2',
    }
    video_dir = touch_dir("tmp/MOOC/Videos/")
    containers = get_containers(context, video_dir, 'flv', None)
    assert len(containers) == 3

@pytest.mark.parametrize(
    'format', [
        'flv', 'mp4', 'm4s'
    ])
def test_parse_segments(format):
    container = BililiContainer(
        id=1,
        name="Unknown",
        path=touch_dir("tmp/MOOC/Videos/video1"),
        meta={
            "avid": '',
            "bvid": '1Y441167U2',
            "cid": '113529568',
        },
        format=format,
    )
    parse_segments(container, quality_sequence_default, block_size=0)
