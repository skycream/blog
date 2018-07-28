<template>
<div>
  <h2>Line</h2>

  <div class="card">
    <header>
      <chartjs-line v-bind:beginzero="beginZero"
        v-bind:labels="labels[radio]"
        v-bind:datalabel="dataLabel"
        v-bind:data="data[radio]"
        v-bind:backgroundcolor="bgColor"
        v-bind:bordercolor="borderColor"
        v-bind:bind="true"/>
    </header>

    <footer class="flex two">
      <label>
        <input type="radio" value="day"
        v-bind:name="dataLabel"
        v-model="radio">
        <span class="checkable">Today</span>
      </label>
      <label>
        <input type="radio" value="week"
        v-bind:name="dataLabel"
        v-model="radio">
        <span class="checkable">This Week</span>
      </label>
    </footer>
  </div>
</div>
</template>

<script>
export default {
  data() {
    return {
      beginZero: true,
      labels: {
        day: [8, 10, 12, 14, 16],
        week: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
      },
      dataLabel: "Foo",
      radio: "day",
      data: {
        day: [1, 3, 5, 3, 1],
        week: [12, 14, 16, 18, 11, 13, 15]
      },
      bgColor: "#ff8a80",
      borderColor: "#f44336"
    };
  }
};
</script>
