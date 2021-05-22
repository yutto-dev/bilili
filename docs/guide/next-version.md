# V2 尝鲜

::: warning

V2 尚处于初期 ALPHA 阶段，部分参数及使用方式尚不稳定。

:::

## 动机

Nyakku 说在最初设计我的时候有很多问题难以解决，所以就重新制作了我的後輩 yutto，yutto 可以完成一些我很难完成的任务。

TODO: 说明 yutto 与 bilili 的不同

## 安装预览版

```bash
pip install --pre yutto
```

## 使用示例

```bash
yutto get https://www.bilibili.com/bangumi/play/ep395211 --vcodec="hevc:copy" --debug
yutto batch get https://www.bilibili.com/bangumi/play/ep395211 --vcodec="hevc:copy" --debug -p 1
```

## 反馈

yutto 尚处于 ALPHA 阶段，希望大家在 [discussion](https://github.com/SigureMo/bilili/discussions/) 中积极反馈～
