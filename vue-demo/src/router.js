import Vue from "vue";
import Router from "vue-router";
Vue.use(Router);

// Layouts
import Default from "./layouts/default";
// import Blank from "./layouts/blank";

// Views
import Aos from "./views/aos";
import GoogleMaps from "./views/google-maps";

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
        },
        {
          path: "/google-maps",
          component: GoogleMaps
        }
      ]
    }
  ]
});
