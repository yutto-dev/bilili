# bilili

<p align="center">
   <a href="https://python.org/" target="_blank"><img alt="python" src="https://img.shields.io/badge/Python-3.6|3.7|3.8-green?logo=python"></a>
   <a href="https://pypi.org/project/bilili/" target="_blank"><img src="https://img.shields.io/pypi/v/bilili" alt="pypi"></a>
   <a href="https://github.com/SigureMo/bilili/actions?query=workflow%3A%22Test+Crawler%22" target="_blank"><img alt="Test Crawler" src="https://github.com/SigureMo/bilili/workflows/Test%20Crawler/badge.svg"></a>
   <a href="LICENSE"><img alt="LICENSE" src="https://img.shields.io/github/license/SigureMo/bilili"></a>
   <a href="https://bilibili.com" target="_blank"><img src="https://img.shields.io/badge/bilibili-1eabc9.svg?logo=bilibili&logoColor=white" alt="Bilibili"></a>
</p>

使用 Python 下载 [B 站](https://www.bilibili.com/)视频，ビリリ~

> 仅限个人学习和研究使用，切勿用于其他用途

## Get Started

`bilili` 可以从以下两种视频主页获取视频

-  普通视频：
   -  `https://www.bilibili.com/video/avxxxxxx`
   -  `https://b23.tv/avxxxxxx`
   -  `https://www.bilibili.com/video/BVxxxxxx`
   -  `https://b23.tv/BVxxxxxx`
-  番剧视频： `https://www.bilibili.com/bangumi/media/mdxxxxxx`

### 安装 FFmpeg

由于大多数格式需要合并，所以 bilili 需要使用 ffmpeg，你需要事先安装好它

Windows 请[手动下载](https://ffmpeg.org/download.html)后，存放到任意目录下，并将该目录**添加到环境变量**

而如果是 `*nix`，可以很方便地通过包管理器一键完成

### 安装 Bilili

``` bash
pip install bilili
```

此外你还可以在 Github 上下载最新的源码

``` bash
git clone git@github.com:SigureMo/bilili.git
pip install -r requirements.txt
```

### 运行

如果你是通过 `pip` 直接安装程序，此时你可以直接使用命令 `bilili` 来进行下载

```
bilili <url>
```

而如果你是通过源码运行，需要在项目根目录运行如下命令

``` bash
python -m bilili.bilili_dl <url>
```

当然，你需要将 `<url>` 替换为前面的视频主页 url

## Options

`bilili` 还支持很多参数，具体如下

-  `-f`/`--format` 选择下载格式（`flv` or `m4s` or `mp4`），默认为 m4s 格式，注意该参数仅代表下载源格式，所有格式最后均会转为 mp4
-  `-d`/`--dir` 指定存储目录，默认为项目根目录
-  `-q`/`--quality` 指定清晰度，默认为 `120`，对应关系如下
   -  `120` # 超清 4K
   -  `116` # 超清 1080P60
   -  `112` # 高清 1080P+
   -  `80` # 高清 1080P
   -  `74` # 高清 720P60
   -  `64` # 高清 720P
   -  `32` # 清晰 480P
   -  `16` # 流畅 360P
      > 如果不存在指定的清晰度，会自动降低到最接近的清晰度
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

## Note

### Download and merge

视频的下载需要包含下载和合并两个过程，如果出现进度条卡在最后一刻一段时间属于正常现象，此时往往在进行合并操作

### Source

由于 m4s 格式下载速度更佳，因此默认使用 m4s 格式，但偶尔有些课程仍然不支持 m4s 格式（~~如 [操作系统\_清华大学(向勇、陈渝)](https://www.bilibili.com/video/BV1js411b7vg)~~，现已支持，但尚不能保证全部资源均已支持），遇到此类资源请手动切换至 flv 格式

此外，还支持直接解析“高清晰度”的 mp4 视频（仅 acg video，而且最新的 4K 等清晰度是获取不到的），无需合并，但是速度很慢，所以事实上也没什么必要去尝试……不建议使用

> 由于现在同时支持三种接口，所以……我暂时懒得继续改进代码，等以后 Flash 接口彻底被取缔的时候，可能会好好整理下代码（如果那时候我还维护的话）

### Danmaku

默认会下载 XML 格式的弹幕，如果想使用 ASS 格式的弹幕（大多数播放器都支持，可以自动加载），可以加参数 `--ass` 自动转换，或者手动在[us-danmaku](https://tiansh.github.io/us-danmaku/bilibili/)转换

另外，程序内自动转换依赖 [danmaku2ass](https://github.com/m13253/danmaku2ass) ，但是并没有将它存放在我的代码里，而是根据需要动态从 github 上下载并加载的

### Playlist

默认生成**相对路径类型**的 **`PotPlayer`** 播放列表，如果你不想使用 `PotPlayer` 的话，可以通过参数来修改

# References

1. [Bilibili - 1033020837](https://github.com/1033020837/Bilibili)
2. [BilibiliVideoDownload - blogwy](https://github.com/blogwy/BilibiliVideoDownload)
3. [BiliUtil](https://github.com/wolfbolin/BiliUtil)
