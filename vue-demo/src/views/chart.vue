<template>
<div>
  <h1>Chart Demo</h1>

  <div class="grid">
    <chart-line/>
    <chart-bar/>
    <chart-doughnut/>
  </div>
</div>
</template>

<script>
import ChartLine from "@/components/chart-line";
import ChartBar from "@/components/chart-bar";
import ChartDoughnut from "@/components/chart-doughnut";

export default {
  components: {
    ChartLine,
    ChartBar,
    ChartDoughnut
  }
};
</script>

<style lang="scss" scoped>
.grid {
  display: grid;
  grid-row-gap: 2rem;
}
</style>
