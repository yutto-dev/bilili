<template>
  <div class="online-parse-tool">
    <input
      class="url-input form-control"
      v-model="biliUrl"
      placeholder="在这里输入视频 url 哦 (ฅ>ω<*ฅ)"
      @keyup.enter="parse"
      autocomplete
      autofocus
    />
    <button class="url-parse form-control" @click="parse">解析</button>
    <select v-model="cid" class="select-part form-control">
      <option disabled value>{{ selectPartText }}</option>
      <option v-if="partList" v-for="item in partList" :value="item.cid">{{
        'P' + item.id + ': ' + item.name
      }}</option>
    </select>
    <div class="error-container" v-show="showError">
      <p>出问题啦～：{{ error }}</p>
    </div>
    <div class="result-container" v-show="showResult">
      <DPlayer :options="options" ref="player" />
      <p>
        解析结果： <a :href="mp4Url" download="result.mp4">右键此处另存为</a>
      </p>
      <textarea name="mp4-result" class="mp4-result form-control" readonly>{{
        mp4Url
      }}</textarea>
      <button class="copy-to-clipboard form-control" @click="copyToClipboard">
        {{ copyButtonText }}
      </button>
    </div>
  </div>
</template>

<script>
import { match } from 'assert'
export default {
  data() {
    return {
      biliUrl: '',
      avid: '',
      bvid: '',
      cid: '',
      name: '',
      bilipi: 'https://bilipi.sigure.xyz/api/v0',
      selectPartText: '请先解析获得选 P 列表',
      partList: [],
      showResult: false,
      options: {
        video: ''
      },
      copyButtonText: '复制到剪贴板',
      dp: null,
      mp4Url: '',
      showError: false,
      error: ''
    }
  },

  mounted() {
    this.dp = this.$refs.player.dp
  },

  methods: {
    parse() {
      const RE_BV_URL = /https?:\/\/(www\.|m\.)?bilibili\.com\/video\/(?<bvid>(BV|bv)\w+)/
      const RE_BV_URL_SHORT = /https?:\/\/b23\.tv\/(?<bvid>(BV|bv)\w+)/
      const RE_AV_URL = /https?:\/\/(www\.|m\.)?bilibili\.com\/video\/av(?<avid>\d+)/
      const RE_AV_URL_SHORT = /https?:\/\/b23\.tv\/av(?<avid>\d+)/
      const matchObj =
        RE_BV_URL.exec(this.biliUrl) ||
        RE_BV_URL_SHORT.exec(this.biliUrl) ||
        RE_AV_URL.exec(this.biliUrl) ||
        RE_AV_URL_SHORT.exec(this.biliUrl)
      if (matchObj) {
        if (matchObj.groups.bvid) {
          this.bvid = matchObj.groups.bvid
        } else if (matchObj.groups.avid) {
          this.avid = matchObj.groups.avid
        }
        const info_api = `${this.bilipi}/acg_video/list?avid=${this.avid}&bvid=${this.bvid}`
        fetch(info_api)
          .then(res => res.json())
          .then(res => {
            if (res.code !== 0) {
              this.error = res.message
              this.showError = true
            } else {
              this.partList = res.data
              this.selectPartText = '点此选 P'
              this.showError = false
            }
          })
      } else {
        this.error = '不支持这样的 URL 哟～'
        this.showError = true
      }
    },

    show() {
      const video_api = `${this.bilipi}/acg_video/playurl?avid=${this.avid}&bvid=${this.bvid}&cid=${this.cid}&type=mp4`
      const danmaku_api = `${this.bilipi}/danmaku/dplayer?cid=${this.cid}`
      fetch(video_api)
        .then(res => res.json())
        .then(res => {
          const mp4Url = res.data[0].url
          this.showResult = true
          this.dp = this.$refs.player.dp
          this.dp.switchVideo({
            url: mp4Url
          })
          this.mp4Url = mp4Url
          this.copyButtonText = '复制到剪贴板'
        })
    },

    copyToClipboard() {
      const textarea = this.$el.querySelector('.mp4-result')
      textarea.select()
      document.execCommand('Copy')
      this.copyButtonText = '复制成功✓'
    }
  },

  watch: {
    cid(val, oldval) {
      this.showResult = false
      this.show()
    }
  }
}
</script>

<style scoped>
.form-control {
  display: block;
  width: 100%;
  height: 2.375rem;
  box-sizing: border-box;
  padding: 0.375rem 0.75rem;
  color: #3f2f9e;
  background-color: #fff;
  background-clip: padding-box;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  margin: 5px 0;
}

.mp4-result {
  height: 10rem;
  resize: none;
}
</style>
