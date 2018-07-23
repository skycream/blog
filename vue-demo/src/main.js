require("dotenv").config();

import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";

import AOS from "aos";
import "aos/dist/aos.css";

import * as VueGoogleMaps from "vue2-google-maps";
Vue.use(VueGoogleMaps, {
  load: { key: process.env.VUE_APP_GOOGLE_MAPS_API_KEY }
});

Vue.config.productionTip = false;

new Vue({
  created() {
    AOS.init({ disable: "phone" });
  },
  router,
  store,
  render: h => h(App)
}).$mount("#app");
