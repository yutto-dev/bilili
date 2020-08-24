export default ({ Vue, options, router, siteData, isServer }) => {
  if (!isServer) {
    const DPlayer = require('./vue-dplayer.js').default
    Vue.component('DPlayer', DPlayer)
    const BililiPlayer = require('./BililiPlayer.vue').default
    Vue.component('BililiPlayer', BililiPlayer)
  }
}
