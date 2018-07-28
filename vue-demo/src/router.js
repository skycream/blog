import Vue from "vue";
import Router from "vue-router";
Vue.use(Router);

// Layouts
import Default from "./layouts/default";
// import Blank from "./layouts/blank";

// Views
import Aos from "./views/aos";
import Ionicons from "./views/ionicons";
import GoogleMaps from "./views/google-maps";
import VueCharts from "./views/vue-charts";

export default new Router({
  mode: "history",
  routes: [
    {
      path: "/",
      component: Default,
      children: [
        { path: "/aos", component: Aos },
        { path: "/google-maps", component: GoogleMaps },
        { path: "/ionicons", component: Ionicons },
        { path: "/vue-charts", component: VueCharts }
      ]
    }
  ]
});
