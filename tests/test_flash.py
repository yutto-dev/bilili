import pytest
from tests.default import config_default
from bilibili import acg_video, bangumi


def test_bilibili_acg_video():
    url = "https://www.bilibili.com/video/BV1Y441167U2/"
    config = dict(config_default)
    config["url"] = url
    acg_video.parse(url, config)


def test_bilibili_bangumi():
    url = "https://www.bilibili.com/bangumi/media/md28223066/"
    config = dict(config_default)
    config["url"] = url
    bangumi.parse(url, config)
