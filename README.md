# bilili

<p align="center">
   <a href="https://python.org/" target="_blank"><img alt="python" src="https://img.shields.io/badge/Python-3.6|3.7|3.8-green?logo=python"></a>
   <a href="https://github.com/SigureMo/bilili/actions?query=workflow%3A%22Test+Crawler%22" target="_blank"><img alt="Test Crawler" src="https://github.com/SigureMo/bilili/workflows/Test%20Crawler/badge.svg"></a>
   <a href="LICENSE"><img alt="LICENSE" src="https://img.shields.io/github/license/SigureMo/bilili"></a>
</p>

使用 Python 下载 [B 站](https://www.bilibili.com/)视频，ビリリ~

> 仅限个人学习和研究使用，切勿用于其他用途

## Get Started

`bilili` 可以从以下两种视频主页获取视频

-  普通视频：
   -  `https://www.bilibili.com/video/avxxxxxx`
   -  `https://b23.tv/avxxxxxx`
   - `https://www.bilibili.com/video/BVxxxxxx`
   - `https://b23.tv/BVxxxxxx`
-  番剧视频： `https://www.bilibili.com/bangumi/media/mdxxxxxx`

首先要**下载 `ffmpeg`**（[下载地址](https://ffmpeg.org/download.html)），存放到任意目录下，并将该目录**添加到环境变量**（如果是 `*nix`，可以很方便地通过包管理器一键完成）

之后**安装依赖**

```bash
pip install -r requirements.txt
```

下载的方式很简单，只需要在终端中运行如下命令即可

```bash
python bilili.py <url>
```

需要将 `<url>` 替换为前面的视频主页 url

## Options

`bilili` 还支持很多参数，具体如下

- `-s`/`--source` 选择播放源（`flash` or `h5`），默认为 html5 播放源
-  `-d`/`--dir` 指定存储目录，默认为项目根目录
-  `-r`/`--sharpness` 指定清晰度，默认为 `120`，对应关系如下
   -  `120` # 超清 4K
   -  `116` # 超清 1080P60
   -  `112` # 高清 1080P+
   -  `80` # 高清 1080P
   -  `74` # 高清 720P60
   -  `64` # 高清 720P
   -  `32` # 清晰 480P
   -  `16` # 流畅 360P
      > 如果不存在对应清晰度，会自动降低到最接近的清晰度
-  `-t`/`--num-thread` 指定最大下载线程数，默认为 30
-  `-p`/`--episodes` 选集，可通过以下方式进行选择，默认为 all
   -  `<p1>` 单独下某一剧集
   -  `<p1>,<p2>,<p3>,...,<pn>` 即通过 `,` 分割，不要加空格
   -  `<p_start>~<p_end>` 即通过 `~` 分隔，下载起始到终止的剧集
   -  `all` 全部下载
-  `-w`/`--overwrite` 强制覆盖已下载视频
-  `-c`/`--sess-data` 传入 `cookies` 中的 `SESSDATA`
-  `--playlist-type` 指定播放列表类型，支持 `dpl` 和 `m3u` ，默认为 `dpl`，设置为 `no` 即不生成播放列表
-  `--path-type` 指定播放列表路径的类型（`rp`：相对路径，`ap`：绝对路径），默认为相对路径
-  `--ass` 自动将 `XML` 弹幕转换为 `ASS` 弹幕
-  `--enable-block` 启用分段下载器
-  `--block-size` 指定分段下载器分块的大小，默认为 128MB

## Tips

### Download and merge

视频的下载需要包含下载和合并两个过程，如果出现进度条卡在最后一刻一段时间属于正常现象，此时往往在进行合并操作

### Source

由于 HTML5 源下载速度更佳，因此默认使用 HTML5 播放源，但偶尔有些课程仍然不支持 HTML5 源（如 [操作系统_清华大学(向勇、陈渝)](https://www.bilibili.com/video/BV1js411b7vg)），遇到此类资源请手动切换至 Flash 源

### Danmaku

默认会下载 XML 格式的弹幕，如果想使用 ASS 格式的弹幕（大多数播放器都支持，可以自动加载），可以加参数 `--ass` 自动转换，或者手动在[us-danmaku](https://tiansh.github.io/us-danmaku/bilibili/)转换

另外，程序内自动转换依赖 [danmaku2ass](https://github.com/m13253/danmaku2ass) ，但是并没有将它存放在我的代码里，而是根据需要动态从 github 上下载并加载的

### Segmented download

下载器内置了分段下载的机制，也即将大文件分成小块下载之后合并，充分利用多线程的优势。但该模块稳定性不高，可能在使用过程中出现一些问题，因此并未作为默认机制启用，如果需要更高的速度请手动开启

未来可能会直接调用 aria2 下载

### Playlist

默认生成**相对路径类型**的 **`PotPlayer`** 播放列表，如果你不想使用 `PotPlayer` 的话，可以通过参数来修改

# Reference

1. [Bilibili - 1033020837](https://github.com/1033020837/Bilibili)
2. [BilibiliVideoDownload - blogwy](https://github.com/blogwy/BilibiliVideoDownload)
