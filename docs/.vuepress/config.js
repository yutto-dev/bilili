module.exports = {
  title: "bilili",
  description: "🍻 bilibili video and danmaku downloader | B站视频、弹幕下载器",

  plugins: [
    // 鼠标特效插件
    [
      "cursor-effects",
      {
        size: 1.75,
        shape: "star"
      }
    ],
    // 离开页面标题变化
    [
      "dynamic-title",
      {
        showText: "(ฅ>ω<*ฅ)欢迎回来！",
        hideText: "( ๑ˊ•̥▵•)੭₎₎不要走呀！",
        recoverTime: 2000
      }
    ]
  ],

  themeConfig: {
    nav: [
      { text: "首页", link: "/" },
      { text: "指南", link: "/guide/" },
      { text: "参数", link: "/options/" }
    ],
    sidebarDepth: 1,
    sidebar: {
      "/guide/": [
        "",
        "getting-started",
        "work-process",
        "faq",
        "sponsor",
        "notice"
      ],
      "/options/": ["", "cli", "usage"]
    },
    repo: "SigureMo/bilili",
    docsDir: "docs",
    docsBranch: "master"
  }
};
