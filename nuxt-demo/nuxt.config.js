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
    link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }]
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
    },
    vendor: ["aos", "vue2-google-maps"]
  },
  modules: ["@nuxtjs/dotenv"],
  plugins: [
    { src: "~/plugins/aos", ssr: false },
    "~/plugins/vue2-google-maps",
    { src: "~/plugins/chart", ssr: false },
    { src: "~/plugins/hchs-vue-charts", ssr: false }
  ],
  css: ["aos/dist/aos.css"]
};
