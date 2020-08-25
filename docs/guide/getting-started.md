# 快速上手

## 视频速览

<BililiPlayer bvid="BV1vZ4y1M7mQ" cid="222200470" :page=2 />

## 我所支持的 url

嘛～我也是比较挑剔的，目前我只支持以下几种视频 url

-  投稿视频主页：
   -  `https://www.bilibili.com/video/avxxxxxx` 嘛，这种 av 号的我会支持
   -  `https://b23.tv/avxxxxxx` 短链接也可以考虑
   -  `https://www.bilibili.com/video/BVxxxxxx` 最新的 bv 号也不错
   -  `https://b23.tv/BVxxxxxx` 当然，它的短链接也可以
-  番剧视频主页：
   -  `https://www.bilibili.com/bangumi/media/mdxxxxxx` 番剧的主页当然可以
   -  `https://www.bilibili.com/bangumi/play/ssxxxxxx` 番剧的播放页（ss 号的）也可以啦
   -  `https://b23.tv/ssxxxxxx` 还有它的短链接
   -  `https://www.bilibili.com/bangumi/play/epxxxxxx` 番剧的播放页（ep 号的）也是可以哒
   -  `https://b23.tv/epxxxxxx` 当然也包括它的短链接啦

## 我的解释器：Python <Badge type="tip" text="3.8+"/>

为了能够正常与你交流，你需要先安装 Python 前辈，当然一定要是 3.8 以上的版本，不然她可能也不知道我在说什么。

如果你是 Windows，请自行去 [Python 官网](https://www.python.org/)下载并安装，安装时记得要勾选 「Add to PATH」选项，不然可能需要你手动添加到环境变量。

`*nix` 的话一般都自带 python 环境，但要注意版本。

## 我的依赖：FFmpeg

由于 B 站给我的视频大多是需要合并的，所以我需要 FFmpeg 小可爱的帮助，你需要事先把她安装到你的电脑上～

如果你所使用的操作系统是 Windows，操作有些些麻烦，你需要[手动下载](https://ffmpeg.org/download.html)她，并将她放到你的环境变量中～

::: details 详细操作

打开下载链接后，在 「Get packages & executable files」 部分选择 Windows 徽标，在 「Windows EXE Files」 下找到 「Windows builds by Zeranoe」 并点击，点击新页面的 「Download Build」 按钮，就开始下载啦～

下载后解压，并随便放到一个安全的地方，然后在文件夹中找到 `ffmpeg.exe`，复制其所在文件夹路径。

右击「此电脑」，选择属性，在其中找到「高级系统设置」 → 「环境变量」，双击 PATH，在其中添加刚刚复制的路径（非 Win10 系统操作略有差异，请自行查阅「环境变量设置」的方法）。

保存保存，完事啦～～～

:::

当然，如果你使用的是 `*nix` 系统的话，直接使用自己的包管理器就能一键完成该过程。

::: details 示例

比如 MacOS 可以使用

```bash
brew install ffmpeg
```

Ubuntu 可以使用

```bash
apt install ffmpeg
```

Manjaro 等 Arch 系可以使用

```bash
pacman -S ffmpeg
```

如此种种，不一一列举。

:::

此时，你可以在终端上使用 `ffmpeg -version` 命令来测试安装是否正确，只要显示的不是 `Command not found` 之类的提示就说明……成功啦～～～

## 召唤 𝓫𝓲𝓵𝓲𝓵𝓲

是时候闪亮登场啦，你可以通过以下两种方式中任意一种方式来召唤我～

### 通过 pip 复制我的镜像

由于我已经在 PyPI 上放置了自己的一份镜像，因此你可以通过 pip 来把那份镜像 copy 到自己电脑上

```bash
pip install bilili
```

### 通过 git 复制我的本体

如果你想见到我的最新版本体，那么你需要从 github 上将我 clone 下来

```bash
git clone git@github.com:SigureMo/bilili.git
cd bilili/
python setup.py build
python setup.py install
```

无论通过哪种方式安装，此时直接使用 `bilili` 命令都应该不再是 `Command not found` 之类的提示啦。

## 开始工作

一切准备就绪，请为我分配任务吧～

当然你只可以指派我可以完成的任务，也就是[我所支持的 url 格式](#我所支持的-url)。

我的工作指派方式非常简单

```bash
bilili <url>
```

当然这里的 `<url>` 需要用前面所说的 `url` 来替换。

::: details 示例

比如下载我的 bilili 演示视频只需要

```bash
bilili https://www.bilibili.com/video/BV1vZ4y1M7mQ
```

下载番剧《雾山五行》只需要

```bash
bilili https://www.bilibili.com/bangumi/media/md28228714
```

:::

如果一切配置正确，此时我应该会正常工作咯。

当然，如果你想了解我的更多功能，请查阅[参数使用](../cli/)部分。
