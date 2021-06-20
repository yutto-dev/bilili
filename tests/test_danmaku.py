import pytest

from bilili.api.danmaku import get_danmaku


@pytest.mark.api
def test_danmaku():
    cid = "144541892"
    get_danmaku(cid=cid)
