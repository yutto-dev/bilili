import pytest

from bilili.api.bangumi import get_season_id, get_bangumi_title, get_bangumi_list, get_bangumi_playurl
from bilili.api.exceptions import CannotDownloadError


def test_get_season_id():
    media_id = "28223066"
    assert get_season_id(media_id=media_id) == "28770"


def test_get_title():
    media_id = "28223066"
    assert get_bangumi_title(media_id=media_id) == "我的三体之章北海传"


def test_get_list():
    season_id = "28770"
    video_list = get_bangumi_list(season_id=season_id)
    assert video_list[0]["cid"] == "144541892"
    assert video_list[0]["avid"] == "84271171"
    assert video_list[0]["bvid"] == "BV1q7411v7Vd"
    assert video_list[0]["episode_id"] == "300998"


@pytest.mark.parametrize("type", ["flv", "dash"])
def test_get_playurl(type):
    avid = "84271171"
    bvid = "BV1q7411v7Vd"
    cid = "144541892"
    episode_id = "300998"
    try:
        play_list = get_bangumi_playurl(avid=avid, bvid=bvid, cid=cid, episode_id=episode_id, quality=120, type=type)
    # 可能 GitHub Action 由于地区限制无法获取
    except CannotDownloadError:
        pass
