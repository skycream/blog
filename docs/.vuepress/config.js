const vueSidebar = [
  "",
  {
    title: "Tutorial",
    collapsable: false,
    children: [
      ["aos", "AOS"]
      // ["axios", "Axios"],
      // ["bootstrap", "Bootstrap"],
      // ["google-maps", "Google Maps"],
      // ["ionicons", "Ionicons"],
      // ["netlify", "Netlify"],
      // ["postcss", "PostCSS"],
      // ["prettier", "Prettier"],
      // ["prism", "Prism"],
      // ["prismic", "Prismic"],
      // ["vue-charts", "Vue Charts"],
      // ["vue-lazyload", "Vue Lazyload"],
      // ["vue-moment", "Vue Moment"],
      // ["vuepress", "Vuepress"],
      // ["vuex", "Vuex"]
    ]
  }
  // {
  //   title: "Walkthrough",
  //   children: [
  //     ["amalia-studio", "Amalia Studio"],
  //     ["tiara-restaurant", "Tiara Restaurant"]
  //   ]
  // }
];

const nuxtSidebar = [
  "",
  {
    title: "Tutorial",
    collapsable: false,
    children: [
      ["aos", "AOS"]
      // ["axios", "Axios"],
      // ["bootstrap", "Bootstrap"],
      // ["google-maps", "Google Maps"],
      // ["ionicons", "Ionicons"],
      // ["netlify", "Netlify"],
      // ["postcss", "PostCSS"],
      // ["prettier", "Prettier"],
      // ["prism", "Prism"],
      // ["prismic", "Prismic"],
      // ["vue-charts", "Vue Charts"],
      // ["vue-lazyload", "Vue Lazyload"],
      // ["vue-moment", "Vue Moment"],
      // ["vuex", "Vuex"]
    ]
  }
  // {
  //   title: "Walkthrough",
  //   children: [
  //     ["azka-bakery", "Azka Bakery"],
  //     ["enlightenment-news", "Enlightenment News"]
  //   ]
  // }
];

module.exports = {
  head: [["link", { rel: "icon", href: "/logo.png" }]],
  ga: "UA-90535731-3",
  serviceWorker: true,
  serviceWorker: {
    updatePopup:
      true | { message: "New content is available.", buttonText: "Refresh" }
  },
  locales: {
    "/": {
      lang: "en",
      title: "Yasmin ZY",
      description: "Building website for your business"
    },
    "/id/": {
      lang: "id",
      title: "Yasmin ZY",
      description: "Membuat website untuk usaha Anda"
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
              { text: "Vue", link: "/vue/" },
              { text: "Nuxt", link: "/nuxt/" }
            ]
          }
        ],
        sidebar: {
          "/vue/": vueSidebar,
          "/nuxt/": nuxtSidebar
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
              { text: "Vue", link: "/id/vue/" },
              { text: "Nuxt", link: "/id/nuxt/" }
            ]
          }
        ],
        sidebar: {
          "/id/vue/": vueSidebar,
          "/id/nuxt/": nuxtSidebar
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
