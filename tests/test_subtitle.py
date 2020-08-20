import pytest

from bilili.api.subtitle import get_subtitle


def test_subtitle():
    bvid = "BV1i741187Dp"
    cid = "149439373"
    get_subtitle(bvid=bvid, cid=cid)
