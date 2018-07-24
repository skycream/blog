<template>
<div>
  <h1>Vue Charts Demo</h1>

  <div class="grid">
    <vue-charts-line/>
    <vue-charts-bar/>
    <vue-charts-doughnut/>
  </div>
</div>
</template>

<script>
import VueChartsLine from "@/components/vue-charts-line";
import VueChartsBar from "@/components/vue-charts-bar";
import VueChartsDoughnut from "@/components/vue-charts-doughnut";

export default {
  components: {
    VueChartsLine,
    VueChartsBar,
    VueChartsDoughnut
  }
};
</script>

<style lang="scss" scoped>
.grid {
  display: grid;
  grid-row-gap: 2rem;
}
</style>
