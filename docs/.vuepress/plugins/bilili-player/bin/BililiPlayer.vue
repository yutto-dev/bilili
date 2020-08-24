<template>
  <div class="dplayer" id="dplayer"></div>
</template>

<script>
import DPlayer from 'dplayer'

export default {
  props: {
    avid: {
      required: false,
      type: String,
      default: ''
    },
    bvid: {
      required: false,
      type: String,
      default: ''
    },
    cid: {
      required: false,
      type: String,
      default: ''
    },
    page: {
      required: false,
      type: Number,
      default: 1
    }
  },
  data() {
    return {
      bilipi: BILIPI,
      dp: null
    }
  },

  mounted() {
    const video_api = `${this.bilipi}/acg_video/playurl?avid=${this.avid}&bvid=${this.bvid}&cid=${this.cid}&type=mp4`
    const danmaku_api = `${this.bilipi}/danmaku/dplayer?cid=${this.cid}`
    let home_url = 'https://www.bilibili.com/video/'
    if (this.avid) {
      home_url += 'av' + this.avid
    } else if (this.bvid) {
      if (this.bvid.substring(0, 2).toLowerCase() !== 'bv') {
        home_url += 'BV'
      }
      home_url += this.bvid
    } else {
      console.log('[BililiPlayer] avid 和 bvid 均未传入！')
    }
    fetch(video_api)
      .then(res => {
        return res.json()
      })
      .then(res => {
        const dp = new DPlayer({
          container: this.$el,
          lang: 'zh-cn',
          video: {
            url: res.data[0].url
          },
          contextmenu: [
            {
              text: '前往 B 站观看',
              link: home_url
            }
          ],
          danmaku: {
            addition: [danmaku_api]
          }
        })
        this.dp = dp
      })
  },

  beforeDestroy() {
    this.dp && this.dp.destroy()
  }
}
</script>

<style scoped></style>
