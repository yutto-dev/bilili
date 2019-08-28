# bilili-dl

![python 3.6.7](https://img.shields.io/badge/python-3.6.7-green?style=flat-square&logo=python)

使用 Python 下载 [B 站](https://www.bilibili.com/)视频，bilililili~

> 仅限个人学习和研究使用，切勿用于其他用途

## Get Started

`bilili-dl` 可以从以下两种视频主页获取视频

-  普通视频： `https://www.bilibili.com/video/avxxxxxx`
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
-  `--playlist-type` 指定播放列表类型，支持 dpl 和 m3u ，默认为 dpl，设置为 no 即不生成播放列表
-  `--path-type` 指定播放列表路径的类型（rp：相对路径，ap：绝对路径），默认为相对路径
-  `--ffmpeg` 指定 `ffmpeg` 存放路径，默认为 `ffmpeg/ffmpeg.exe`
-  `--override` 强制覆盖已下载视频
- `--ass` 自动将 XML 弹幕转换为 ASS 弹幕

## Kanck

默认会下载 XML 格式的弹幕，如果想使用 ASS 格式的弹幕（大多数播放器都支持，可以自动加载），可以加参数 `--ass` 自动转换，或者手动在[us-danmaku](https://tiansh.github.io/us-danmaku/bilibili/)转换

> 程序内自动转换依赖 [danmaku2ass](https://github.com/m13253/danmaku2ass) ，但是并没有将它存放在我的代码里，而是根据需要动态从 github 上下载并加载的

## Blog

具体实现见[使用 Python 爬取 B 站视频](https://www.sigure.xyz/Posts/17_bilili_dl.html)

# Reference

1. [Bilibili 视频爬取](https://github.com/1033020837/Bilibili)
