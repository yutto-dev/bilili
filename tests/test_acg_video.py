import pytest

from bilili.api.acg_video import (
    get_acg_video_list,
    get_acg_video_playurl,
    get_acg_video_subtitle,
    get_acg_video_title,
    get_video_info,
)


@pytest.mark.api
def test_get_video_info():
    bvid = "BV1vZ4y1M7mQ"
    assert get_video_info(bvid=bvid)["bvid"] == bvid


@pytest.mark.api
def test_get_title():
    bvid = "BV1vZ4y1M7mQ"
    assert get_acg_video_title(bvid=bvid) == "用 bilili 下载 B 站视频"


@pytest.mark.api
def test_get_list():
    bvid = "BV1vZ4y1M7mQ"
    video_list = get_acg_video_list(bvid=bvid)
    assert video_list[0]["cid"] == "222190584"
    assert video_list[1]["cid"] == "222200470"


@pytest.mark.api
@pytest.mark.ci_skip
@pytest.mark.parametrize("type", ["flv", "mp4", "dash"])
def test_get_playurl(type: str):
    bvid = "BV1vZ4y1M7mQ"
    cid = "222190584"
    play_list = get_acg_video_playurl(bvid=bvid, cid=cid, quality=120, audio_quality=30280, type=type)


@pytest.mark.api
def test_get_subtitle():
    bvid = "BV1i741187Dp"
    cid = "149439373"
    get_acg_video_subtitle(bvid=bvid, cid=cid)
