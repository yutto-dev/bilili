# API <Badge type="tip" text="v0"/> <Badge type="warning" text="beta"/>

除去基本的下载功能，你还可以通过我的一些 API 完成更多操作，比如通过 Python 来调用 `bilili.api` 模块，或者直接使用 WSGI 方式来调用，该 API 部署在 Vercel 上，你可以通过 <https://bilipi.sigure.xyz/api/v0> 来调用。

## 投稿视频

[`bilili.api.acg_video`](https://github.com/SigureMo/bilili/blob/master/bilili/api/acg_video.py)

### 获取视频信息

-  Python 调用： `bilili.api.acg_video.get_video_info`
-  WSGI 调用： <https://bilipi.sigure.xyz/api/v0/video_info>
-  参数： `avid`, `bvid`

### 获取视频标题

-  Python 调用： `bilili.api.acg_video.get_acg_video_title`
-  WSGI 调用： <https://bilipi.sigure.xyz/api/v0/acg_video/title>
-  参数： `avid`, `bvid`

### 获取视频列表

-  Python 调用： `bilili.api.acg_video.get_acg_video_list`
-  WSGI 调用： <https://bilipi.sigure.xyz/api/v0/acg_video/list>
-  参数： `avid`, `bvid`

### 获取视频播放地址

-  Python 调用： `bilili.api.acg_video.get_acg_video_playurl`
-  WSGI 调用： <https://bilipi.sigure.xyz/api/v0/acg_video/playurl>
-  参数： `avid`, `bvid`, `cid`, `quality`, `type`

## 番剧

[`bilili.api.bangumi`](https://github.com/SigureMo/bilili/blob/master/bilili/api/bangumi.py)

### 获取 `season_id`

-  Python 调用： `bilili.api.bangumi.get_season_id`
-  WSGI 调用： <https://bilipi.sigure.xyz/api/v0/get_season_id>
-  参数： `media_id`

### 获取视频标题

-  Python 调用： `bilili.api.bangumi.get_bangumi_title`
-  WSGI 调用： <https://bilipi.sigure.xyz/api/v0/bangumi/title>
-  参数： `media_id`, `season_id`, `episode_id`

### 获取视频列表

-  Python 调用： `bilili.api.bangumi.get_bangumi_list`
-  WSGI 调用： <https://bilipi.sigure.xyz/api/v0/bangumi/list>
-  参数： `episode_id`, `season_id`

### 获取视频播放地址

-  Python 调用： `bilili.api.bangumi.get_bangumi_playurl`
-  WSGI 调用： <https://bilipi.sigure.xyz/api/v0/bangumi/playurl>
-  参数： `avid`, `bvid`, `episode_id`, `cid`, `quality`, `type`

## 弹幕

[`bilili.api.danmaku`](https://github.com/SigureMo/bilili/blob/master/bilili/api/danmaku.py)

### 获取 XML 弹幕

-  Python 调用： `bilili.api.danmaku`
-  WSGI 调用： <https://bilipi.sigure.xyz/api/v0/danmaku>
-  参数： `cid`

## 字幕

[`bilili.api.subtitle`](https://github.com/SigureMo/bilili/blob/master/bilili/api/subtitle.py)

### 获取 srt 字幕

-  Python 调用： `bilili.api.subtitle`
-  WSGI 调用： <https://bilipi.sigure.xyz/api/v0/subtitle>
-  参数： `avid`, `bvid`, `cid`
