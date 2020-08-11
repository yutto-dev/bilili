<template>
  <a
    :href="link"
    :alt="username"
    :title="username"
    target="_blank"
    class="user"
  >
    <img :src="avatarUrl" :title="username" class="avatar" />
  </a>
</template>

<script>
export default {
  props: {
    username: {
      required: true,
      type: String
    },
    avatar: {
      required: false,
      type: String,
      default: ''
    }
  },

  data() {
    return {
      link: `https://github.com/${this.username}`,
      avatarUrl: this.avatar
        ? this.avatar
        : `https://github.com/${this.username}.png`
    }
  }
}
</script>

<style scoped>
.user {
  margin: 10px 10px;
  display: inline-block;
}

.avatar {
  border-radius: 50%;
  width: 100%;
  height: 100%;
  width: 54px;
  height: 54px;
}
</style>
