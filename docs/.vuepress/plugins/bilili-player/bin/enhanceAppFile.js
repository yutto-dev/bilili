import 'vue-dplayer/dist/vue-dplayer.css'

import BililiPlayer from './BililiPlayer.vue'

export default ({ Vue, options, router, siteData, isServer }) => {
  if (!isServer) {
    const DPlayer = require('vue-dplayer')
    Vue.component('DPlayer', DPlayer)
  }
  Vue.component('BililiPlayer', BililiPlayer)
}
