import { ThemeConfig } from 'vuepress-theme-vt'
import { defineConfig4CustomTheme } from 'vuepress/config'
import path from 'path'

const bilili_versions: {
  bilili: string
  yutto: string
} = JSON.parse(process.env.BILILI_VERSIONS)

export default defineConfig4CustomTheme<ThemeConfig>({
  title: 'bilili',
  description: '🍻 bilibili video and danmaku downloader',
  locales: {
    '/': {
      lang: 'zh-CN',
      title: 'bilili',
      description: '🍻 B站视频、弹幕下载器',
    },
  },

  head: [
    ['meta', { property: 'og:url', content: 'https://bilili.nyakku.moe' }],
    ['meta', { property: 'og:site_name', content: 'bilili' }],
    ['meta', { property: 'og:image', content: '/logo.png' }],
    [
      'meta',
      {
        property: 'og:description',
        content: '🍻 bilibili video and danmaku downloader | B站视频、弹幕下载器',
      },
    ],
    ['meta', { property: 'og:title', content: 'bilili' }],
  ],

  // @ts-ignore
  plugins: [
    // 返回顶部
    ['@vuepress/back-to-top'],
    // 鼠标特效插件
    [
      'cursor-effects',
      {
        size: 1.75,
        shape: 'star',
      },
    ],
    // 离开页面标题变化
    [
      'dynamic-title',
      {
        showText: '(๑‾᷅^‾᷅๑)哼，还知道回来！',
        hideText: '(〟-_・)ﾝ?这就走了？',
        recoverTime: 2000,
      },
    ],
  ],

  theme: 'vt',
  themeConfig: {
    enableDarkMode: true,
    nav: [
      { text: '首页', link: '/' },
      { text: '指南', link: '/guide/' },
      { text: '参数', link: '/cli/' },
      {
        text: `v${bilili_versions.bilili}`,
        items: [
          {
            text: `v${bilili_versions.yutto}`,
            link: 'https://github.com/yutto-dev/yutto',
          },
        ],
      },
      {
        text: '支持我',
        items: [
          { text: '赞助', link: '/sponsor' },
          {
            text: '参与贡献',
            link: 'https://github.com/yutto-dev/bilili/blob/main/CONTRIBUTING.md',
          },
        ],
      },
    ],
    // @ts-ignore
    sidebar: {
      '/guide/': [
        {
          title: '指南',
          collapsable: false,
          children: ['', 'getting-started', 'knack'],
        },
        {
          title: '深入',
          collapsable: false,
          children: ['cli', 'work-process'],
        },
        'faq',
        'feedback',
        'notice',
        'thanks',
      ],
    },
    repo: 'yutto-dev/bilili',
    docsDir: 'docs',
    docsBranch: 'main',
    editLinks: true,
    editLinkText: '啊，我说错了？你可以帮我纠正哦～',
  },

  // 插件 API 提供的额外路由
  additionalPages: [
    {
      path: '/guide/cli.html',
      filePath: path.resolve(__dirname, '../cli/README.md'),
    },
  ],
})
