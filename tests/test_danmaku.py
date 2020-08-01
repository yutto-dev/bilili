import pytest

from bilili.api.danmaku import get_danmaku
from bilili.utils.base import touch_dir
from bilili.video import BililiContainer


def test_danmaku():
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
    get_danmaku(container)
