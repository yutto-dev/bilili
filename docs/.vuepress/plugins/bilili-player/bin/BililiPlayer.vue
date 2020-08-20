<template>
  <DPlayer :options="options" ref="player" />
</template>

<script>
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
      dp: null,
      options: {
        lang: 'zh-cn',
        video: {
          url: ''
        }
      }
    }
  },

  mounted() {
    this.dp = this.$refs.player.dp
    const url = `${this.bilipi}/acg_video/playurl?avid=${this.avid}&bvid=${this.bvid}&cid=${this.cid}&type=mp4`
    fetch(url)
      .then(res => {
        return res.json()
      })
      .then(res => {
        this.dp.switchVideo({
          url: res.result[0].url
        })
      })
  },

  beforeDestroy() {
    this.dp && this.dp.destroy()
  }
}
</script>

<style scoped></style>
