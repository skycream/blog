const tutorialSidebar = [
  "",
  ["aos", "AOS"],
  // ["axios", "Axios"],
  // ["bootstrap", "Bootstrap"],
  ["google-maps", "Google Maps"],
  ["ionicons", "Ionicons"],
  // ["netlify", "Netlify"],
  // ["postcss", "PostCSS"],
  ["prettier", "Prettier"],
  // ["prism", "Prism"],
  // ["prismic", "Prismic"],
  ["vue-charts", "Vue Charts"]
  // ["vue-lazyload", "Vue Lazyload"],
  // ["vue-moment", "Vue Moment"],
  // ["vuepress", "Vuepress"],
  // ["vuex", "Vuex"]
];

const projectSidebar = [
  ""
  // ["amalia-studio", "Amalia Studio"],
  // ["azka-bakery", "Azka Bakery"],
  // ["enlightenment-news", "Enlightenment News"],
  // ["tiara-restaurant", "Tiara Restaurant"]
];

module.exports = {
  head: [["link", { rel: "icon", href: "/logo.png" }]],
  ga: "UA-90535731-3",
  locales: {
    "/": {
      lang: "en",
      title: "Yasmin ZY",
      description: "Building a website for your business."
    },
    "/id/": {
      lang: "id",
      title: "Yasmin ZY",
      description: "Membuat website untuk usaha Anda."
    }
  },
  themeConfig: {
    locales: {
      "/": {
        selectText: "Languages",
        label: "English",
        lastUpdated: "Last updated",
        nav: [
          { text: "Home", link: "/" },
          { text: "Portfolio", link: "/portfolio" },
          {
            text: "Blog",
            items: [
              { text: "Tutorial", link: "/tutorial/" },
              { text: "Project", link: "/project/" }
            ]
          }
        ],
        sidebar: {
          "/tutorial/": tutorialSidebar,
          "/project/": projectSidebar
        }
      },
      "/id/": {
        selectText: "Bahasa",
        label: "Indonesia",
        editLinkText: "Sunting halaman ini",
        lastUpdated: "Terakhir diperbarui",
        nav: [
          { text: "Beranda", link: "/id/" },
          { text: "Portofolio", link: "/id/portfolio" },
          {
            text: "Blog",
            items: [
              { text: "Tutorial", link: "/id/tutorial/" },
              { text: "Proyek", link: "/id/project/" }
            ]
          }
        ],
        sidebar: {
          "/id/tutorial/": tutorialSidebar,
          "/id/project/": projectSidebar
        }
      }
    },
    repo: "yasminzy/blog",
    docsDir: "docs",
    editLinks: true
  },
  markdown: {
    lineNumbers: true
  }
};
