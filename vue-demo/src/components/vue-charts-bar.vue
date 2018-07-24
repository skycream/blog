<template>
<div>
  <h2>Bar</h2>

  <div class="card">
    <canvas id="fooCanvas" count="2"></canvas>

    <chartjs-bar v-for="(item, index) in types"
      v-bind:key="index"
      target="fooCanvas"
      v-bind:beginzero="beginZero"
      v-bind:labels="labels"
      v-bind:datalabel="item.dataLabel"
      v-bind:data="item.data"
      v-bind:backgroundcolor="item.bgColor"
      v-bind:bordercolor="item.borderColor"
      v-bind:bind="true"/>
  </div>
</div>
</template>

<script>
export default {
  data() {
    return {
      beginZero: true,
      labels: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
      types: [
        {
          dataLabel: "Bar",
          data: [1, 3, 5, 7, 2, 4, 6],
          bgColor: "#ff80ab",
          borderColor: "#e91e63"
        },
        {
          dataLabel: "Baz",
          data: [1, 5, 2, 6, 3, 7, 4],
          bgColor: "#ea80fc",
          borderColor: "#9c27b0"
        }
      ]
    };
  }
};
</script>
