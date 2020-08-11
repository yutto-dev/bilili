const path = require("path");

module.exports = {
  title: "bilili",
  description: "🍻 bilibili video and danmaku downloader | B站视频、弹幕下载器",
  locales: {
    "/": {
      lang: "zh-CN",
    },
  },

  head: [
    ["meta", { property: "og:url", content: "https://bilili.sigure.xyz" }],
    ["meta", { property: "og:site_name", content: "bilili" }],
    ["meta", { property: "og:image", content: "/logo.png" }],
    [
      "meta",
      {
        property: "og:description",
        content:
          "🍻 bilibili video and danmaku downloader | B站视频、弹幕下载器",
      },
    ],
    ["meta", { property: "og:title", content: "bilili" }],
  ],

  plugins: [
    // 返回顶部
    ["@vuepress/back-to-top"],
    // 鼠标特效插件
    [
      "cursor-effects",
      {
        size: 1.75,
        shape: "star",
      },
    ],
    // 离开页面标题变化
    [
      "dynamic-title",
      {
        showText: "(๑‾᷅^‾᷅๑)哼，还知道回来！",
        hideText: "(〟-_・)ﾝ?这就走了？",
        recoverTime: 2000,
      },
    ],
  ],

  themeConfig: {
    nav: [
      { text: "首页", link: "/" },
      { text: "指南", link: "/guide/" },
      { text: "参数", link: "/cli/" },
      {
        text: "支持我",
        items: [
          { text: "赞助", link: "/sponsor" },
          {
            text: "参与贡献",
            link:
              "https://github.com/SigureMo/bilili/blob/master/CONTRIBUTING.md",
          },
        ],
      },
    ],
    sidebarDepth: 1,
    sidebar: {
      "/guide/": [
        {
          title: "指南",
          collapsable: false,
          sidebarDepth: 1,
          children: ["", "getting-started", "knack"],
        },
        {
          title: "深入",
          collapsable: false,
          sidebarDepth: 1,
          children: ["cli", "work-process"],
        },
        "faq",
        "feedback",
        "notice",
      ],
      "/cli/": "auto",
    },
    repo: "SigureMo/bilili",
    docsDir: "docs",
    docsBranch: "master",
    editLinks: true,
    editLinkText: "帮我改进我的风格！",
  },

  // 作为插件的额外路由
  additionalPages: [
    {
      path: "/guide/cli.html",
      filePath: path.resolve(__dirname, "../cli/README.md"),
    },
  ],
};
