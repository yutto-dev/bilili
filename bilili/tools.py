import re

from bilili.common.aria2 import Aria2
from bilili.common.ffmpeg import FFmpeg
from bilili.common.crawler import BililiCrawler

aria2 = Aria2(show_progress=True)
ffmpeg = FFmpeg()
spider = BililiCrawler()

regex_acg_video_av = re.compile(r"https?://www.bilibili.com/video/av(?P<avid>\d+)")
regex_acg_video_av_short = re.compile(r"https?://b23.tv/av(?P<avid>\d+)")
regex_acg_video_bv = re.compile(r"https?://www.bilibili.com/video/(bv|BV)(?P<bvid>\w+)")
regex_acg_video_bv_short = re.compile(r"https?://b23.tv/(bv|BV)(?P<bvid>\w+)")
regex_bangumi = re.compile(r"https?://www.bilibili.com/bangumi/media/md(\d+)")
