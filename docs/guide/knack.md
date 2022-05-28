# 使用技巧

## 使用 PotPlayer

PotPlayer 是一款 Windows 下十分强大的播放器，我默认生成的播放列表格式就是 PotPlayer 专用的播放列表格式 `dpl`，你可以使用 PotPlayer 直接打开它。

当然，我并不会强制你使用 PotPlayer（话说其它系统也没有 PotPlayer 的说），因此其它系统请使用[参数 `--playlist-type`](../cli#指定播放列表类型) 进行修改。

## 终端的选择

请尽量使用支持 emoji 的终端，不然在我向你传达信息时可能出现失真问题（「乱码」现象），但这并不会影响下载过程。

Windows 比较推荐使用 「Windows Terminal」，或者如果你有 VS Code 这样的自带终端的编辑器也是可以直接使用其终端的。

## 断点续传功能的使用

由于我具备断点续传的功能，因此你不必担心下载过程的中断，你可以在任何时刻 `Ctrl + C` 中断下载，下一次重新启动只需要重新运行一下上次的命令即可。

当然你也可以在重新开始时修改一部分参数，但由于断点续传功能会依赖于本地已下载部分的大小直接接着下载，因此如果你在一次下载中途停止后，修改了 `type`、`block-size`、`quality` 参数再次让我下载的话，两次下载的内容将截然不同，但断点续传机制仍然会强制拼接在一起，为了避免该问题，请在修改相关参数时删除已下载部分，或者直接添加参数 `overwrite` 来自动完成该过程。

## 升级方式

如果你是通过 pip 安装我的话，那么只需要使用

```bash
pip install --upgrade bilili
```

而如果你是使用 git 直接安装，直接重新运行安装时所使用的命令即可。

## 定义命令别名

可能你不想每次运行 bilili 都输入各种各样参数，所以这里我建议你将常用的参数都记录成在一条 alias 里，比如 Nyakku 就是这样做的

```bash
alias bll='bilili -d ~/Movies/bilili/ -c `cat ~/.sessdata` --disable-proxy --danmaku=ass --playlist-type=m3u -y --use-mirrors'
```

由于 Nyakku 使用的是 zsh，将其存到 `~/.zshrc` 就好了，如果你使用的是 bash 的话，存到 `~/.bashrc` 就好。

当然，Nyakku 是将自己 Cookie 里的 SESSDATA 存到了 `~/.sessdata`，这样每次只需运行 bll 就可以省去定义存储目录、Cookie 等等的参数啦。
