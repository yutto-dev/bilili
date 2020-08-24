/**
 * ref: https://github.com/MoePlayer/vue-dplayer/blob/master/src/index.js
 */

import DPlayer from 'dplayer'

const VueDPlayer = {
  props: {
    options: {
      type: Object
    }
  },

  data() {
    return {
      dp: null
    }
  },

  mounted() {
    this.options.container = this.$el
    const player = (this.dp = new DPlayer(this.options))
    const events = player.events
    Object.keys(events).forEach(item => {
      if (item === 'events') {
        return false
      } else {
        events[item].forEach(event => {
          player.on(event, () => this.$emit(event))
        })
      }
    })
  },

  beforeDestroy() {
    this.dp && this.dp.destroy()
  },

  install(Vue, { name = 'DPlayer' } = {}) {
    Vue.component(name, this)
  },

  render(h) {
    return h(
      'div',
      {
        class: 'dplayer'
      },
      []
    )
  }
}

export default VueDPlayer
