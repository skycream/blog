module.exports = {
  head: {
    title: "Nuxt Demo - Yasmin ZY",
    meta: [
      { charset: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      {
        hid: "description",
        name: "description",
        content: "Nuxt.js project demo"
      }
    ],
    link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
    script: [{ src: "https://unpkg.com/ionicons/dist/ionicons.js", body: true }]
  },
  loading: { color: "#2196F3" },
  build: {
    extend(config, { isDev, isClient }) {
      if (isDev && isClient) {
        config.module.rules.push({
          enforce: "pre",
          test: /\.(js|vue)$/,
          loader: "eslint-loader",
          exclude: /(node_modules)/
        });
      }
    }
  },
  modules: ["@nuxtjs/dotenv"],
  plugins: [
    "~/plugins/google-maps",
    "~/plugins/prism",
    { src: "~/plugins/aos", ssr: false },
    { src: "~/plugins/chart", ssr: false }
  ]
};
