import Vue from "vue";
import Router from "vue-router";
Vue.use(Router);

// Layouts
import Default from "./layouts/default";
// import Blank from "./layouts/blank";

// Views
import Aos from "./views/aos";
import Chart from "./views/chart";
import GoogleMaps from "./views/google-maps";
import Ionicons from "./views/ionicons";
import Prism from "./views/prism";

export default new Router({
  mode: "history",
  routes: [
    {
      path: "/",
      component: Default,
      children: [
        { path: "/aos", component: Aos },
        { path: "/chart", component: Chart },
        { path: "/google-maps", component: GoogleMaps },
        { path: "/ionicons", component: Ionicons },
        { path: "/prism", component: Prism }
      ]
    }
  ]
});
