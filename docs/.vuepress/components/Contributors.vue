<template>
  <div class="github-contributors">
    <GithubUser
      v-for="contributor in contributors"
      :username="contributor.login"
      :avatar="contributor.avatar_url"
    />
  </div>
</template>

<script>
import GithubUser from './GithubUser.vue'
export default {
  props: {
    owner: {
      required: true,
      type: String
    },
    repo: {
      required: true,
      type: String
    }
  },

  data() {
    return {
      contributors: Object.create(null)
    }
  },

  mounted() {
    const url = `https://api.github.com/repos/${this.owner}/${this.repo}/contributors`
    fetch(url)
      .then(response => {
        return response.json()
      })
      .then(res => {
        return res.filter(contributor => {
          return !contributor.login.endsWith('[bot]')
        })
      })
      .then(res => {
        this.contributors = res
      })
  }
}
</script>

<style scoped></style>
