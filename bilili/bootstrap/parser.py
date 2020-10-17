import sys
import os

from bilili.utils.attrdict import AttrDict
from bilili.utils.base import repair_filename, touch_dir, touch_file, size_format
from bilili.utils.playlist import Dpl, M3u
from bilili.utils.subtitle import Subtitle
from bilili.tools import spider, ass, regex
from bilili.video import BililiContainer
from bilili.bootstrap.common import parse_episodes
from bilili.api.subtitle import get_subtitle
from bilili.api.danmaku import get_danmaku
from bilili.api.exceptions import (
    ArgumentsError,
    CannotDownloadError,
    UnknownTypeError,
    UnsupportTypeError,
    IsPreviewError,
)


def parse_containers(options):
    options = options >> AttrDict()
    # 匹配资源的 id 以及其对应所属类型
    # fmt: off
    resource_id = {
        "avid": "",
        "bvid": "",
        "episode_id": "",
        "season_id": "",
    } >> AttrDict()

    # fmt: off
    if (avid_match := regex.acg_video.av.origin.match(options.uri)) or \
        (avid_match := regex.acg_video.av.short.match(options.uri)):
        from bilili.api.acg_video import get_video_info
        avid = avid_match.group("avid")
        if episode_id := get_video_info(avid=avid)["episode_id"]:
            resource_id.episode_id = episode_id
        else:
            resource_id.avid = avid
    elif (bvid_match := regex.acg_video.bv.origin.match(options.uri)) or \
        (bvid_match := regex.acg_video.bv.short.match(options.uri)):
        from bilili.api.acg_video import get_video_info
        bvid = bvid_match.group("bvid")
        if episode_id := get_video_info(bvid=bvid)["episode_id"]:
            resource_id.episode_id = episode_id
        else:
            resource_id.bvid = bvid
    elif media_id_match := regex.bangumi.md.origin.match(options.uri):
        from bilili.api.bangumi import get_season_id
        media_id = media_id_match.group("media_id")
        resource_id.season_id = get_season_id(media_id=media_id)
    elif (episode_id_match := regex.bangumi.ep.origin.match(options.uri)) or \
        (episode_id_match := regex.bangumi.ep.short.match(options.uri)):
        episode_id = episode_id_match.group("episode_id")
        resource_id.episode_id = episode_id
    elif (season_id_match := regex.bangumi.ss.origin.match(options.uri)) or \
        (season_id_match := regex.bangumi.ss.short.match(options.uri)):
        season_id = season_id_match.group("season_id")
        resource_id.season_id = season_id
    else:
        print("视频地址有误！")
        sys.exit(1)

    if resource_id.avid or resource_id.bvid:
        from bilili.parser.acg_video import get_title, get_list, get_playurl
        bili_type = "acg_video"
    elif resource_id.season_id or resource_id.episode_id:
        from bilili.parser.bangumi import get_title, get_list, get_playurl
        bili_type = "bangumi"

    # 对爬取器进行配置
    spider.set_cookies({
        "SESSDATA": options.sess_data
    })
    if options.disable_proxy:
        spider.trust_env = False

    # 获取标题
    title = get_title(resource_id)
    print(title)

    # 创建所需目录结构
    base_dir = touch_dir(os.path.join(options.dir, repair_filename(title + " - bilibili")))
    video_dir = touch_dir(os.path.join(base_dir, "Videos"))

    # 获取需要的信息
    containers = [BililiContainer(video_dir=video_dir, type=options.type, **video) for video in get_list(resource_id)]

    # 解析并过滤不需要的选集
    episodes = parse_episodes(options.episodes, len(containers))
    containers, containers_need_filter = [], containers
    for container in containers_need_filter:
        if container.id not in episodes:
            container._.downloaded = True
            container._.merged = True
        else:
            containers.append(container)

    # 初始化播放列表
    if options.playlist_type == "dpl":
        playlist = Dpl(os.path.join(base_dir, "Playlist.dpl"), path_type="AP" if options.abs_path else "RP")
    elif options.playlist_type == "m3u":
        playlist = M3u(os.path.join(base_dir, "Playlist.m3u"), path_type="AP" if options.abs_path else "RP")
    else:
        playlist = None

    # 解析片段信息及视频 url
    for i, container in enumerate(containers):
        print(
            "{:02}/{:02} parsing segments info...".format(i + 1, len(containers)), end="\r",
        )

        # 解析视频 url
        try:
            for playinfo in get_playurl(container, options.quality, options.audio_quality):
                container.append_media(
                    block_size=options.block_size * 1024 * 1024,
                    **playinfo
                )
        except CannotDownloadError as e:
            print('[warn] {} 无法下载，原因：{}'.format(container.name, e.message))
        except IsPreviewError:
            print('[warn] {} 是预览视频'.format(container.name))

        # 写入播放列表
        if playlist is not None:
            playlist.write_path(container.path)

        # 下载弹幕
        if bili_type == "acg_video":
            for sub_info in get_subtitle(avid=resource_id.avid, bvid=resource_id.bvid, cid=container.meta['cid']):
                sub_path = '{}_{}.srt'.format(os.path.splitext(container.path)[0], sub_info['lang'])
                subtitle = Subtitle(sub_path)
                for sub_line in sub_info['lines']:
                    subtitle.write_line(sub_line["content"], sub_line["from"], sub_line["to"])

        # 生成弹幕
        if options.danmaku != "no":
            with open(os.path.splitext(container.path)[0] + ".xml", 'w', encoding='utf-8') as f:
                f.write(get_danmaku(container.meta['cid']))

        # 转换弹幕为 ASS
        if options.danmaku == "ass":
            ass.convert_danmaku_from_xml(
                os.path.splitext(container.path)[0] + ".xml", container.height, container.width,
            )
    if playlist is not None:
        playlist.flush()

    return containers
