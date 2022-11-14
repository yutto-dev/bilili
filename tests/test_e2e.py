import subprocess
import sys

import pytest

from bilili.__version__ import VERSION as bilili_version

PYTHON = sys.executable


@pytest.mark.e2e
def test_version_e2e():
    p = subprocess.run([PYTHON, "-m", "bilili", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    res = p.stdout.decode()
    assert res.strip().endswith(bilili_version)


@pytest.mark.e2e
def test_ui_e2e():
    p = subprocess.run(
        [PYTHON, "-m", "bilili.utils.console.ui"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
    )


@pytest.mark.e2e
@pytest.mark.ci_skip
def test_bangumi_e2e():
    short_bangumi = "https://www.bilibili.com/bangumi/play/ep100367"
    p = subprocess.run(
        [PYTHON, "-m", "bilili", short_bangumi, "-p=^", "-q=16", "-y", "-w"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


@pytest.mark.e2e
def test_acg_video_e2e():
    short_acg_video = "https://www.bilibili.com/video/BV1AZ4y147Yg"
    p = subprocess.run(
        [PYTHON, "-m", "bilili", short_acg_video, "-q=16", "-y", "-w"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


@pytest.mark.e2e
def test_acg_video_8k_e2e():
    acg_video_8k = "https://www.bilibili.com/video/BV1qM4y1w716"
    p = subprocess.run(
        [PYTHON, "-m", "bilili", acg_video_8k, "-q=127", "-y", "-c=*****"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
