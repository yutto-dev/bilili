const { resolve } = require('path')

module.exports = (options = {}, context) => ({
  define() {
    const { bilipi = 'https://bilipi.sigure.xyz/api/v0' } = options

    return {
      BILIPI: bilipi
    }
  },

  enhanceAppFiles: resolve(__dirname, './bin/enhanceAppFile.js')
})
