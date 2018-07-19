import Vue from "vue";
import Router from "vue-router";
Vue.use(Router);

// Layouts
import Default from "./layouts/default";
// import Blank from "./layouts/blank";

// Views
import Aos from "./views/aos.vue";

export default new Router({
  mode: "history",
  routes: [
    {
      path: "/",
      component: Default,
      children: [
        {
          path: "/aos",
          component: Aos
        }
      ]
    }
  ]
});
