import pytest
from tests.default import config_default
from bilibili_mp4 import acg_video


def test_bilibili_acg_video():
    url = "https://www.bilibili.com/video/BV1Y441167U2/"
    config = dict(config_default)
    config["url"] = url
    acg_video.parse(url, config)
