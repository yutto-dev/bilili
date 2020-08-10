<template>
  <div>
    <iframe
      :src="url"
      scrolling="no"
      border="0"
      frameborder="no"
      framespacing="0"
      allowfullscreen="true"
    ></iframe>
  </div>
</template>

<script>
export default {
  props: {
    avid: {
      required: false,
      type: String,
      default: "",
    },
    bvid: {
      required: false,
      type: String,
      default: "",
    },
    cid: {
      required: false,
      type: String,
      default: "",
    },
    page: {
      required: false,
      type: Number,
      default: 1,
    },
  },
  data() {
    if (this.avid === "" && this.bvid === "") {
      console.log("avid 和 bvid 同时空缺！");
    }
    let video_url = "//player.bilibili.com/player.html?high_quality=1";
    if (this.avid) {
      video_url += "&aid=" + this.avid;
    }
    if (this.bvid) {
      video_url += "&bvid=" + this.bvid;
    }
    // 移动端必须指定 cid 字段才能解析到正确的视频
    if (this.cid) {
      video_url += "&cid=" + this.cid;
    }
    if (this.page) {
      video_url += "&page=" + this.page;
    }
    console.log(video_url);
    return {
      url: video_url,
    };
  },
};
</script>

<style scoped>
div {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 75%;
}

iframe {
  position: absolute;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
}
</style>
