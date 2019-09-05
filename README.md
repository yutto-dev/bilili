# bilili-dl

![python 3.6.7](https://img.shields.io/badge/python-3.6.7-green?style=flat-square&logo=python)

使用 Python 下载 [B 站](https://www.bilibili.com/)视频，bilililili~

> 仅限个人学习和研究使用，切勿用于其他用途

## Get Started

`bilili-dl` 可以从以下两种视频主页获取视频

-  普通视频： 
   - `https://www.bilibili.com/video/avxxxxxx`
   - `https://b23.tv/avxxxxx`
-  番剧视频： `https://www.bilibili.com/bangumi/media/mdxxxx`

在下视频之前，首先要配置好 `ffmpeg` ，随便在网上下一个就好，存放在 `/ffmpeg/ffmpeg.exe` （也可以存放在其他路径，之后在参数中指定路径即可）

之后安装依赖

```bash
pip install -r requirements.txt
```

下载的方式很简单，只需要在终端中运行如下命令即可

```bash
python bilili-dl.py <url>
```

需要将 `<url>` 替换为前面的视频主页 url

## More

`bilili-dl` 还支持很多参数，具体如下

-  `-d`/`--dir` 指定存储目录，默认为根目录
-  `-r`/`--sharpness` 指定清晰度，默认为 112，对应关系如下
   -  112 # 高清 1080P+
   -  80 # 高清 1080P
   -  64 # 高清 720P
   -  32 # 清晰 480P
   -  16 # 流畅 360P
-  `-t`/`--num-thread` 指定最大下载线程数，默认为 10
-  `-p`/`--episodes` 选集，可通过以下方式进行选择，默认为 all
   -  `<p1>` 单独下某一剧集
   -  `<p1>,<p2>,<p3>,...,<pn>` 即通过 `,` 分割，不要加空格
   -  `<p_start>~<p_end>` 即通过 `~` 分隔，下载起始到终止的剧集
   -  `all` 全部下载
-  `-w`/`--overwrite` 强制覆盖已下载视频
- `-c`/`--sess-data` 传入 cookies 中的 SESSDATA
-  `--playlist-type` 指定播放列表类型，支持 dpl 和 m3u ，默认为 dpl，设置为 no 即不生成播放列表
-  `--path-type` 指定播放列表路径的类型（rp：相对路径，ap：绝对路径），默认为相对路径
-  `--ffmpeg` 指定 `ffmpeg` 存放路径，默认为 `ffmpeg/ffmpeg.exe`
- `--ass` 自动将 XML 弹幕转换为 ASS 弹幕
- `--no-block` 不使用分段下载器
- `--segment-size` 指定分段下载器分块的大小

## Kanck

### Danmaku

默认会下载 XML 格式的弹幕，如果想使用 ASS 格式的弹幕（大多数播放器都支持，可以自动加载），可以加参数 `--ass` 自动转换，或者手动在[us-danmaku](https://tiansh.github.io/us-danmaku/bilibili/)转换

> 程序内自动转换依赖 [danmaku2ass](https://github.com/m13253/danmaku2ass) ，但是并没有将它存放在我的代码里，而是根据需要动态从 github 上下载并加载的

### Segment-dl

使用分段下载器能够获得更高的速度，在 B 站默认分段数不多的情况下，每个线程下载速度非常慢，大概也就 300K/s ，分段下载器会在每个分段的基础上继续分块，充分利用多线程的优势进行下载，极大提高下载速度，但由于优化不足，可能会出现一些问题（比如因为某一个块连接出现问题而导致整个片段迟迟不合并，不过有着断点续传的机制，重新运行一次就可以只下载缺少的块了），如果觉得分段下载不可靠可以使用 `--no-block` 关闭该功能

## Blog

具体实现见[使用 Python 爬取 B 站视频](https://www.sigure.xyz/Posts/17_bilili_dl.html)

# Reference

1. [Bilibili 视频爬取](https://github.com/1033020837/Bilibili)
