import pytest
import subprocess
import sys

from bilili.__version__ import VERSION as bilili_version

PYTHON = sys.executable


@pytest.mark.e2e
def test_version_e2e():
    p = subprocess.run([PYTHON, "-m", "bilili", "-v"], stdout=subprocess.PIPE)
    res = p.stdout.decode()
    assert res.strip().endswith(bilili_version)


@pytest.mark.e2e
def test_ui_e2e():
    subprocess.run([PYTHON, "-m", "bilili.utils.console.ui"], stdout=subprocess.PIPE)


@pytest.mark.e2e
def test_bangumi_e2e():
    short_bangumi = "https://www.bilibili.com/bangumi/play/ep100367"
    subprocess.run([PYTHON, "-m", "bilili", short_bangumi, "-p=^", "-y"], stdout=subprocess.PIPE)


@pytest.mark.e2e
def test_acg_video_e2e():
    short_acg_video = "https://www.bilibili.com/video/BV1AZ4y147Yg"
    subprocess.run([PYTHON, "-m", "bilili", short_acg_video, "-y"], stdout=subprocess.PIPE)
