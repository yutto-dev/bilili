# bilili

<p align="center">
   <a href="https://python.org/" target="_blank"><img alt="python" src="https://img.shields.io/badge/Python-3.6|3.7|3.8-green?logo=python"></a>
   <a href="https://pypi.org/project/bilili/" target="_blank"><img src="https://img.shields.io/pypi/v/bilili" alt="pypi"></a>
   <a href="https://github.com/SigureMo/bilili/actions?query=workflow%3A%22API+Test%22" target="_blank"><img alt="Test Crawler" src="https://github.com/SigureMo/bilili/workflows/API%20Test/badge.svg"></a>
   <a href="LICENSE"><img alt="LICENSE" src="https://img.shields.io/github/license/SigureMo/bilili"></a>
   <a href="https://bilibili.com" target="_blank"><img src="https://img.shields.io/badge/bilibili-1eabc9.svg?logo=bilibili&logoColor=white" alt="Bilibili"></a>
   <a href="https://gitmoji.carloscuesta.me"><img src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg?style=flat-square" alt="Gitmoji"></a>
</p>

使用 Python 下载 [B 站](https://www.bilibili.com/)视频，ビリリ~

> 仅限个人学习和研究使用，切勿用于其他用途

## 快速开始

`bilili` 可以从以下两种视频主页获取视频

-  普通视频主页：
   -  `https://www.bilibili.com/video/avxxxxxx`
   -  `https://b23.tv/avxxxxxx`
   -  `https://www.bilibili.com/video/BVxxxxxx`
   -  `https://b23.tv/BVxxxxxx`
-  番剧视频主页（非播放页面，在播放页面点一下封面即可跳转）： `https://www.bilibili.com/bangumi/media/mdxxxxxx`

### 安装 FFmpeg

由于大多数格式需要合并，所以 bilili 依赖于 ffmpeg，你需要事先安装好它

Windows 请[手动下载](https://ffmpeg.org/download.html)后，存放到任意目录下，并将 `ffmpeg.exe` 所在目录**添加到环境变量**

而如果是 `*nix`，可以很方便地通过包管理器一键完成

你可以通过直接在终端运行 `ffmpeg -version` 测试是否安装成功

### 安装 Bilili

#### pip 安装

现在 bilili 支持通过 pip 一键安装

``` bash
pip install bilili
```

#### 源码安装

此外你还可以从 Github 上下载最新的源码进行安装

``` bash
git clone git@github.com:SigureMo/bilili.git
cd bilili/
python setup.py build
python setup.py install # 可能需要 sudo
```

### 运行

运行非常简单～

``` bash
bilili <url>
```

当然，你需要将 `<url>` 替换为前面的视频主页 url

### 调试

<details>

<summary> 本地调试 </summary>

``` bash
git clone git@github.com:SigureMo/bilili.git
cd bilili/
pip install -r requirements.txt
python -m bilili.bilili_dl <url>
```

</details>

## 参数

`bilili` 还支持很多参数，具体如下

-  `-f`/`--format` 选择下载格式（`flv` or `m4s` or `mp4`），默认为 m4s 格式，注意该参数仅代表下载源格式，所有格式最后均会转为 mp4
-  `-d`/`--dir` 指定存储目录，默认为项目根目录
-  `-q`/`--quality` 指定清晰度，默认为 `120`，对应关系如下
   |code|清晰度|
   |:-:|:-:|
   |120|超清 4K|
   |116|超清 1080P60|
   |112|高清 1080P+|
   |80|高清 1080P|
   |74|高清 720P60|
   |64|高清 720P|
   |32|清晰 480P|
   |16|流畅 360P|
   |6|极速 240P|
   |208|未知，MP4 格式专属，无法作为参数指定|
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
-  `--danmaku` 指定弹幕类型，支持 `xml` 和 `ass`，如果设置为 `no` 则不下载弹幕，默认为 `xml` 弹幕


<details>

<summary>参数的使用</summary>

参数的使用很简单，比如修改格式为 `flv`，只需要

``` bash
bilili <url> --format=flv
# 或者
bilili <url> -f flv
```

不需要指定具体值，只切换 `True` or `False` 的参数也不需要在命令中指定值，比如开启强制覆盖已下载视频选项

``` bash
bilili <url> --overwrite
# 或者
bilili <url> -w
```

</details>

## 注意事项

### 视频格式

视频格式是指 bilibili 直接提供的资源格式，本程序最终都会转换成通用的 mp4 格式方便观看，不同格式在通用性、下载速度等方面的比较如下

||M4S|FLV|MP4|
|:-:|:-:|:-:|:-:|
|支持程度|中（少数视频不支持）|高|低（仅支持 acg_video）|
|下载速度|高|低|中|
|需要 FFmpeg 合并|是|是|否|
|清晰度支持|全面|中（部分较新的 4K 等清晰度无法获取）|极少（仅支持 1080P 及更低的清晰度，且无法选择）|
|总结|B 站当前使用的格式，拥有齐全的清晰度和最佳的下载速度|当 M4S 无法下载时的备用选项，但大多数视频也在支持|除了不需要合并，一无是处|

### 高清晰度下载

如果你想下载大会员才能看的清晰度，请先确保你是大会员，本程序不会帮助你去获取你没有权限获取的视频

而如果你已经是大会员，登录帐号后，在 B 站按 F12 开启控制台，切换到 Network 选项卡，刷新页面，在第一个资源（往往是 html）的 Header -> cookie 中找到 `SESSDATA` 字段，并通过相关参数传入程序即可

### 弹幕

默认会下载 XML 格式的弹幕，如果想使用 ASS 格式的弹幕（大多数播放器都支持，可以自动加载），可以加参数 `--danmaku=ass` 自动转换，或者手动在[us-danmaku](https://tiansh.github.io/us-danmaku/bilibili/)转换

另外，程序内自动转换依赖 [danmaku2ass](https://github.com/m13253/danmaku2ass) ，但是并没有将它存放在我的代码里，而是根据需要动态从 github 上下载并加载的

### 播放列表

默认生成**相对路径类型**的 **`PotPlayer`** 播放列表，如果你不想使用 `PotPlayer` 的话，可以通过参数来修改

# 参考项目

1. [Bilibili - 1033020837](https://github.com/1033020837/Bilibili)
2. [BilibiliVideoDownload - blogwy](https://github.com/blogwy/BilibiliVideoDownload)
3. [BiliUtil](https://github.com/wolfbolin/BiliUtil)
