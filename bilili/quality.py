from typing import List

quality_sequence_default = [120, 116, 112, 80, 74, 64, 32, 16]

quality_map = {
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
    }
}


def gen_quality_sequence(quality: int = 120) -> List[int]:
    """ 根据默认先降后升的清晰度机制生成清晰度序列 """
    return quality_sequence_default[quality_sequence_default.index(quality):] + list(
        reversed(quality_sequence_default[:quality_sequence_default.index(quality)]))
