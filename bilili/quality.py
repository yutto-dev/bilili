from enum import Enum
from typing import List


class Media(Enum):
    VIDEO = 0
    AUDIO = 30200


video_quality_sequence_default = [127, 125, 120, 116, 112, 80, 74, 64, 32, 16]
audio_quality_sequence_default = [30280, 30232, 30216]

video_quality_map = {
    127: {
        "description": "8K 超高清",
        "width": 8192,
        "height": 4320,
    },
    125: {
        "description": "HDR 真彩",
        "width": 3840,
        "height": 1920,
    },
    120: {
        "description": "4K 超清",
        "width": 3840,
        "height": 1920,
    },
    116: {
        "description": "1080P 60帧",
        "width": 2160,
        "height": 1080,
    },
    112: {
        "description": "1080P 高码率",
        "width": 2160,
        "height": 1080,
    },
    80: {
        "description": "1080P 高清",
        "width": 2160,
        "height": 1080,
    },
    74: {
        "description": "720P 60帧",
        "width": 1440,
        "height": 720,
    },
    64: {
        "description": "720P 高清",
        "width": 1440,
        "height": 720,
    },
    32: {
        "description": "480P 清晰",
        "width": 960,
        "height": 480,
    },
    16: {
        "description": "360P 流畅",
        "width": 720,
        "height": 360,
    },
    6: {
        "description": "240P 极速",
        "width": 320,
        "height": 240,
    },
    208: {
        "description": "1080P 高清",
        "width": 1920,
        "height": 1080,
    },
    192: {
        "description": "720P 高清",
        "width": 1280,
        "height": 720,
    },
}

audio_quality_map = {
    30280: {
        "description": "320kbps",
        "bitrate": 320,
    },
    30232: {
        "description": "128kbps",
        "bitrate": 128,
    },
    30216: {
        "description": "64kbps",
        "bitrate": 64,
    },
    0: {"description": "Unknown", "bitrate": 0},
}


def gen_quality_sequence(quality: int = 127, type: Media = Media.VIDEO) -> List[int]:
    """根据默认先降后升的清晰度机制生成清晰度序列"""
    quality_sequence_default = {
        Media.VIDEO: video_quality_sequence_default,
        Media.AUDIO: audio_quality_sequence_default,
    }[type]
    return quality_sequence_default[quality_sequence_default.index(quality) :] + list(
        reversed(quality_sequence_default[: quality_sequence_default.index(quality)])
    )
