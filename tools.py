from common.aria2 import Aria2
from common.ffmpeg import FFmpeg
from common.crawler import BililiCrawler

aria2 = Aria2(show_progress=True)
ffmpeg = FFmpeg()
spider = BililiCrawler()
