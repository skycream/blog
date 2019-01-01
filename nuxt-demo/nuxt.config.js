const pkg = require("./package");

module.exports = {
  mode: "universal",
  head: {
    title: pkg.name,
    meta: [
      { charset: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { hid: "description", name: "description", content: pkg.description }
    ],
    link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
    script: [{ src: "https://unpkg.com/ionicons/dist/ionicons.js", body: true }]
  },
  loading: { color: "#2196F3" },
  plugins: [
    "~/plugins/google-maps",
    "~/plugins/prism",
    { src: "~/plugins/aos", ssr: false },
    { src: "~/plugins/chart", ssr: false }
  ],
  modules: ["@nuxtjs/dotenv"],
  build: {
    extend(config, ctx) {
      if (ctx.isDev && ctx.isClient) {
        config.module.rules.push({
          enforce: "pre",
          test: /\.(js|vue)$/,
          loader: "eslint-loader",
          exclude: /(node_modules)/
        });
      }
    }
  }
};
