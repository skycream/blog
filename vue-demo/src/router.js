import Vue from "vue";
import Router from "vue-router";
Vue.use(Router);

// Layouts
import Default from "./layouts/default";
// import Blank from "./layouts/blank";

// Views
import Index from "./views/index";

export default new Router({
  base: process.env.BASE_URL,
  mode: "history",
  routes: [
    {
      path: "/",
      component: Default,
      children: [
        { path: "", component: Index },
        { path: "aos", component: () => import("./views/aos") },
        { path: "chart", component: () => import("./views/chart") },
        { path: "google-maps", component: () => import("./views/google-maps") },
        { path: "ionicons", component: () => import("./views/ionicons") },
        { path: "prism", component: () => import("./views/prism") }
      ]
    }
  ]
});
