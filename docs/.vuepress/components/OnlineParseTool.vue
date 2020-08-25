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
      <option disabled value>{{ parts.defaultText }}</option>
      <option v-if="parts.list" v-for="item in parts.list" :value="item.cid">{{
        'P' + item.id + ': ' + item.name
      }}</option>
    </select>
    <div class="error-container" v-show="error.show">
      <p>出问题啦～：{{ error.message }}</p>
    </div>
    <div class="result-container" v-show="result.show">
      <DPlayer :options="result.dplayer.options" ref="player" />
      <p>
        解析结果：
        <a :href="result.mp4Url">右键此处另存为</a>
      </p>
      <textarea name="mp4-result" class="mp4-result form-control" readonly>{{
        result.mp4Url
      }}</textarea>
      <button class="copy-to-clipboard form-control" @click="copyToClipboard">
        {{ result.copyButtonText }}
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
      parts: {
        defaultText: '请先解析获得选 P 列表',
        list: []
      },
      result: {
        show: false,
        dplayer: {
          ref: null,
          options: {
            video: {}
          }
        },
        mp4Url: '',
        copyButtonText: '复制到剪贴板'
      },
      error: {
        show: false,
        message: ''
      }
    }
  },

  mounted() {
    this.result.dplayer.ref = this.$refs.player.dp
  },

  methods: {
    parse() {
      this.cid = ''
      this.hideResult()
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
        this.parts.defaultText = '解析中……'
        fetch(info_api)
          .then(res => res.json())
          .then(res => {
            if (res.code !== 0) {
              this.parts.defaultText = '出了点问题呜～'
              this.showError(res.message)
            } else {
              this.parts.list = res.data
              this.parts.defaultText = '点此选 P'
              this.showError = false
              this.hideError()
            }
          })
      } else {
        this.showError('不支持这样的 URL 哟～')
      }
    },

    showError(message) {
      this.error.show = true
      this.error.message = message
    },

    hideError() {
      this.error.show = false
    },

    showResult() {
      const video_api = `${this.bilipi}/acg_video/playurl?avid=${this.avid}&bvid=${this.bvid}&cid=${this.cid}&type=mp4`
      const danmaku_api = `${this.bilipi}/danmaku/dplayer?cid=${this.cid}`
      fetch(video_api)
        .then(res => res.json())
        .then(res => {
          const mp4Url = res.data[0].url
          this.result.dplayer.ref.switchVideo({
            url: mp4Url
          })
          this.result.mp4Url = mp4Url
          this.result.copyButtonText = '复制到剪贴板'
          this.result.show = true
        })
    },

    hideResult() {
      this.result.show = false
    },

    copyToClipboard() {
      const textarea = this.$el.querySelector('.mp4-result')
      textarea.select()
      document.execCommand('Copy')
      this.result.copyButtonText = '复制成功✓'
      setTimeout(() => {
        this.result.copyButtonText = '复制到剪贴板'
      }, 3000)
    }
  },

  watch: {
    cid(val, oldval) {
      this.hideResult()
      if (this.cid) {
        this.showResult()
      }
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
  background-color: rgba(18, 241, 230, 0.247);
  background-clip: padding-box;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  margin: 5px 0;
}

.mp4-result {
  height: 8rem;
  resize: none;
}
</style>
