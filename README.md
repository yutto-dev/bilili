# bilili-dl

bilililili~

使用 Python 下载 B 站视频，仅限个人学习和研究使用，切勿用于其他用途

## Get Started

`bilili-dl` 可以从以下两种视频主页获取视频

- 普通视频： `https://www.bilibili.com/video/avxxxxxx`
- 番剧视频： `https://www.bilibili.com/bangumi/media/mdxxxx`

在下视频之前，首先要配置好 `ffmpeg` ，随便在网上下一个就好，存放在 `/ffmpeg/ffmpeg.exe` （也可以存放在其他路径，之后在参数中指定路径即可）

下载的方式很简单，只需要在终端中运行如下命令即可

``` bash
python bilili-dl.py <url>
```

需要将 `<url>` 替换为前面的视频主页 url

## More

`bilili-dl` 还支持很多参数，具体如下

- `-d` 指定存储目录，默认为根目录
- `-r` 指定清晰度，默认为 80，对应关系如下
   - 80 # 高清 1080P
   - 64 # 高清 720P
   - 32 # 清晰 480P
   - 16 # 流畅 360P
- `-t` 指定最大下载线程数，默认为 10
- `--playlist-type` 指定播放列表类型，支持 dpl 和 m3u ，默认为 dpl
- `--path-type` 指定播放列表路径的类型（rp：相对路径，ap：绝对路径），默认为相对路径
- `--ffmpeg` 指定 `ffmpeg` 存放路径，默认为 `ffmpeg/ffmpeg.exe`

具体实现见[使用 Python 爬取 B 站视频](https://siguremo.github.io/notev/Posts/17_bilili_dl.html)

# Reference

1. [Bilibili 视频爬取](https://github.com/1033020837/Bilibili)