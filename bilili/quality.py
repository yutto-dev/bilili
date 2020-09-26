from typing import List
from enum import Enum


class Media(Enum):
    VIDEO = 0
    AUDIO = 30200


video_quality_sequence_default = [120, 116, 112, 80, 74, 64, 32, 16]
audio_quality_sequence_default = [30280, 30232, 30216]

video_quality_map = {
    120: {
        "description": "超清 4K",
        "width": 4096,
        "height": 2160,
    },
    116: {
        "description": "高清 1080P60",
        "width": 1920,
        "height": 1080,
    },
    112: {
        "description": "高清 1080P+",
        "width": 1920,
        "height": 1080,
    },
    80: {
        "description": "高清 1080P",
        "width": 1920,
        "height": 1080,
    },
    74: {
        "description": "高清 720P60",
        "width": 1280,
        "height": 720,
    },
    64: {
        "description": "高清 720P",
        "width": 1280,
        "height": 720,
    },
    32: {
        "description": "清晰 480P",
        "width": 640,
        "height": 480,
    },
    16: {
        "description": "流畅 360P",
        "width": 480,
        "height": 360,
    },
    6: {
        "description": "极速 240P",
        "width": 320,
        "height": 240,
    },
    208: {
        "description": "高清 1080P",
        "width": 1920,
        "height": 1080,
    },
    192: {
        "description": "高清 720P",
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


def gen_quality_sequence(quality: int = 120, type: Media = Media.VIDEO) -> List[int]:
    """ 根据默认先降后升的清晰度机制生成清晰度序列 """
    quality_sequence_default = {
        Media.VIDEO: video_quality_sequence_default,
        Media.AUDIO: audio_quality_sequence_default,
    }[type]
    return quality_sequence_default[quality_sequence_default.index(quality) :] + list(
        reversed(quality_sequence_default[: quality_sequence_default.index(quality)])
    )
