# 参数的使用方法

如果你并不经常使用命令行工具，那么可能需要我指点一下参数的使用方法，但如果你经常使用命令行工具的话，这部分直接跳过就好

## 指定参数值

比如你需要修改下载格式为 flv，只需要

```bash
bilili <url> --format=flv
# 或者
bilili <url> -f flv
```

## 切换 `True` or `False`

对于那些不需要指定具体值，只切换 `True` or `False` 的参数，你也不需要在命令中指定值，比如开启强制覆盖已下载视频选项

```bash
bilili <url> --overwrite
# 或者
bilili <url> -w
```

## 多参数同时使用

直接向后加即可，而且 `<url>` 和其它参数都不强制要求顺序，比如下面这些命令都是合法的

```bash
bilili <url> --overwrite --format=flv
bilili --overwrite -f flv <url>
bilili -w <url> --format=flv
```
