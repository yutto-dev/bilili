import re

from bilili.utils.ffmpeg import FFmpeg
from bilili.utils.crawler import BililiCrawler
from bilili.utils.danmaku import ASS
from bilili.events.middleware import DownloaderMiddleware


ffmpeg = FFmpeg()
spider = BililiCrawler()
ass = ASS()
global_middleware = DownloaderMiddleware()


regex_acg_video_av = re.compile(r"https?://www.bilibili.com/video/av(?P<avid>\d+)")
regex_acg_video_av_short = re.compile(r"https?://b23.tv/av(?P<avid>\d+)")
regex_acg_video_bv = re.compile(r"https?://www.bilibili.com/video/(bv|BV)(?P<bvid>\w+)")
regex_acg_video_bv_short = re.compile(r"https?://b23.tv/(bv|BV)(?P<bvid>\w+)")
regex_bangumi = re.compile(r"https?://www.bilibili.com/bangumi/media/md(\d+)")
