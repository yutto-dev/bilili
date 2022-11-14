import pytest

from bilili.api.bangumi import (
    get_bangumi_list,
    get_bangumi_playurl,
    get_bangumi_subtitle,
    get_bangumi_title,
    get_season_id,
)
from bilili.api.exceptions import CannotDownloadError


@pytest.mark.api
def test_get_season_id():
    media_id = "28223066"
    assert get_season_id(media_id=media_id) == "28770"


@pytest.mark.api
def test_get_title():
    media_id = "28223066"
    assert get_bangumi_title(media_id=media_id) == "我的三体之章北海传"


@pytest.mark.api
def test_get_list():
    season_id = "28770"
    video_list = get_bangumi_list(season_id=season_id, with_section=False)
    assert video_list[0]["cid"] == "144541892"
    assert video_list[0]["avid"] == "84271171"
    assert video_list[0]["bvid"] == "BV1q7411v7Vd"
    assert video_list[0]["episode_id"] == "300998"


@pytest.mark.api
@pytest.mark.ci_skip
@pytest.mark.parametrize("type", ["flv", "dash"])
def test_get_playurl(type: str):
    avid = "84271171"
    bvid = "BV1q7411v7Vd"
    cid = "144541892"
    episode_id = "300998"
    play_list = get_bangumi_playurl(
        avid=avid,
        bvid=bvid,
        cid=cid,
        episode_id=episode_id,
        quality=120,
        audio_quality=30280,
        type=type,
    )


@pytest.mark.api
def test_get_subtitle():
    # TODO: 暂未找到需要字幕的番剧（非港澳台）
    pass
