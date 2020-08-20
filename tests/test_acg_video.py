import pytest

from bilili.api.acg_video import get_video_info, get_acg_video_title, get_acg_video_list, get_acg_video_playurl


def test_get_video_info():
    bvid = "BV1vZ4y1M7mQ"
    assert get_video_info(bvid=bvid)["bvid"] == bvid


def test_get_title():
    bvid = "BV1vZ4y1M7mQ"
    assert get_acg_video_title(bvid=bvid) == "用 bilili 下载 B 站视频"


def test_get_list():
    bvid = "BV1vZ4y1M7mQ"
    video_list = get_acg_video_list(bvid=bvid)
    assert video_list[0]["cid"] == "222190584"
    assert video_list[1]["cid"] == "222200470"


@pytest.mark.parametrize("type", ["flv", "mp4", "dash"])
def test_get_playurl(type):
    bvid = "BV1vZ4y1M7mQ"
    cid = "222190584"
    play_list = get_acg_video_playurl(bvid=bvid, cid=cid, quality=120, type=type)
