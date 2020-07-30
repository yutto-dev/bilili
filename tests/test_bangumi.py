import pytest
from api.bangumi import get_title, get_context, get_containers, parse_segments
from common.base import touch_dir
from downloader import BililiContainer


def test_get_title():
    url = "https://www.bilibili.com/bangumi/media/md28223066/"
    assert get_title(url) == "我的三体之章北海传"

def test_get_context():
    url = "https://www.bilibili.com/bangumi/media/md28223066/"
    context = get_context(url)
    assert context["season_id"] == '28770'

def test_get_containers():
    context = {
        "season_id": '28770',
    }
    video_dir = touch_dir("tmp/ThreeBody/Videos/")
    containers = get_containers(context, video_dir, 'flv', None)
    assert len(containers) == 9

@pytest.mark.parametrize(
    'format', [
        'flv', 'm4s'
    ])
def test_parse_segments(format):
    container = BililiContainer(
        id=1,
        name="Unknown",
        path=touch_dir("tmp/ThreeBody/Videos/video1"),
        meta={
            "aid": 84271171,
            "cid": 144541892,
            "epid": 300998,
            "bvid": '',
        },
        format=format,
    )
    parse_segments(container, [120, 116, 112, 80, 74, 64, 32, 16, 6])
