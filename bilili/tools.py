import re

from bilili.utils.crawler import BililiCrawler
from bilili.utils.danmaku import ASS
from bilili.events.middleware import DownloaderMiddleware
from bilili.utils.attrdict import AttrDict


# avid
regex_acg_video_av = re.compile(
    r"https?://www.bilibili.com/video/av(?P<avid>\d+)")
regex_acg_video_av_short = re.compile(r"https?://b23.tv/av(?P<avid>\d+)")

# bvid
regex_acg_video_bv = re.compile(
    r"https?://www.bilibili.com/video/(?P<bvid>(bv|BV)\w+)")
regex_acg_video_bv_short = re.compile(r"https?://b23.tv/(?P<bvid>(bv|BV)\w+)")

# media id
regex_bangumi_md = re.compile(
    r"https?://www.bilibili.com/bangumi/media/md(?P<media_id>\d+)")

# episode id
regex_bangumi_ep = re.compile(
    r"https?://www.bilibili.com/bangumi/play/ep(?P<episode_id>\d+)")
regex_bangumi_ep_short = re.compile(r"https?://b23.tv/ep(?P<episode_id>\d+)")

# season id
regex_bangumi_ss = re.compile(
    r"https?://www.bilibili.com/bangumi/play/ss(?P<season_id>\d+)")
regex_bangumi_ss_short = re.compile(r"https?://b23.tv/ss(?P<season_id>\d+)")


spider = BililiCrawler()
ass = ASS()
global_middleware = DownloaderMiddleware()
regex = {
    'acg_video': {
        'av': {
            'origin': regex_acg_video_av,
            'short': regex_acg_video_av_short,
        },
        'bv': {
            'origin': regex_acg_video_bv,
            'short': regex_acg_video_bv_short,
        },
    },
    'bangumi': {
        'md': {
            'origin': regex_bangumi_md,
        },
        'ep': {
            'origin': regex_bangumi_ep,
            'short': regex_bangumi_ep_short,
        },
        'ss': {
            'origin': regex_bangumi_ss,
            'short': regex_bangumi_ss_short,
        }
    }
} >> AttrDict()
