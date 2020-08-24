<template>
  <div class="online-parse-tool">
    <input v-model="biliUrl" placeholder="在这里输入视频 url 哦 (ฅ>ω<*ฅ)" />
    <button @click="parse">解析</button>
    <br />
    <select v-model="cid">
      <option disabled value="">选 P</option>
      <option
        v-if="partList"
        v-for="item in partList"
        :value="item.cid"
        @click="play"
        >{{ item.id + ': ' + item.name }}</option
      >
    </select>
    <p>result: {{ biliUrl }}</p>
    <br />
    <p>cid: {{ cid }}</p>
    <DPlayer :options="options" ref="player" />
    <p>解析结果： {{ mp4Url }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      biliUrl: '',
      avid: '',
      bvid: '',
      cid: '',
      bilipi: 'https://bilipi.sigure.xyz/api/v0',
      partList: [],
      options: {
        video: ''
      },
      dp: null,
      mp4Url: ''
    }
  },

  mounted() {
    this.dp = this.$refs.player.dp
  },

  methods: {
    parse() {
      const RE_BV_URL = /https?:\/\/www\.bilibili\.com\/video\/(?<bvid>(BV|bv)\w+)/
      const matchObj = RE_BV_URL.exec(this.biliUrl)
      if (matchObj) {
        this.bvid = matchObj.groups.bvid
        const info_api = `${this.bilipi}/acg_video/list?avid=${this.avid}&bvid=${this.bvid}`
        console.log(info_api)
        fetch(info_api)
          .then(res => res.json())
          .then(res => {
            this.partList = res.data
          })
      }
    },

    play() {
      const video_api = `${this.bilipi}/acg_video/playurl?avid=${this.avid}&bvid=${this.bvid}&cid=${this.cid}&type=mp4`
      const danmaku_api = `${this.bilipi}/danmaku/dplayer?cid=${this.cid}`
      console.log(this.dp)
      fetch(video_api)
        .then(res => res.json())
        .then(res => {
          const mp4Url = res.data[0].url
          this.dp.switchVideo({
            url: mp4Url
          })
          this.mp4Url = mp4Url
        })
    }
  },

  watch: {
    cid(val, oldval) {
      this.play()
    }
  }
}
</script>

<style></style>
