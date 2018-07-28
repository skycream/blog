require("dotenv").config();

import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";

import AOS from "aos";
import "aos/dist/aos.css";

import "chart.js";
import "hchs-vue-charts";
Vue.use(window.VueCharts);

import * as VueGoogleMaps from "vue2-google-maps";
Vue.use(VueGoogleMaps, {
  load: { key: process.env.VUE_APP_GOOGLE_MAPS_API_KEY }
});

import "prismjs";
import "prismjs/themes/prism-funky.css";
import "prismjs/components/prism-scss.min";
import "prismjs/plugins/autolinker/prism-autolinker.min";
import "prismjs/plugins/autolinker/prism-autolinker.css";
import Prism from "vue-prism-component";
Vue.component("prism", Prism);

Vue.config.productionTip = false;

new Vue({
  created() {
    AOS.init({ disable: "phone" });
  },
  router,
  store,
  render: h => h(App)
}).$mount("#app");
