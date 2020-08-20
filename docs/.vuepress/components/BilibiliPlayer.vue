<template>
  <div id="dplayer" class="dplayer"></div>
</template>

<script>
import DPlayer from 'dplayer'

export default {
  props: {
    bilipi: {
      required: false,
      type: String,
      default: `https://bilipi.sigure.xyz/api/v0`
    },
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
      dp: null
    }
  },

  mounted() {
    const url = `${this.bilipi}/acg_video/playurl?avid=${this.avid}&bvid=${this.bvid}&cid=${this.cid}&type=mp4`
    fetch(url)
      .then((res) => {
        return res.json()
      })
      .then((res) => {
        this.dp = new DPlayer({
          container: document.getElementById('dplayer'),
          lang: 'zh-cn',
          video: {
            url: res.result[0].url
          }
        })
      })
  }
}
</script>

<style scoped></style>
