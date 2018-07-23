<template>
<div>
  <h1>Google Maps Demo</h1>

  <gmap-map
    v-bind:center="center"
    v-bind:zoom="5"
    v-bind:map-type-id="mapTypeId">
    <gmap-marker
      v-for="(item, index) in markers"
      v-bind:key="index"
      v-bind:position="item.position"
      v-on:click="center=item.position"/>
  </gmap-map>
</div>
</template>

<script>
export default {
  data() {
    return {
      center: { lat: -3.350235, lng: 111.995865 },
      mapTypeId: "terrain",
      markers: [
        { position: { lat: -0.48585, lng: 117.1466 } },
        { position: { lat: -6.21462, lng: 106.84513 } }
      ]
    };
  }
};
</script>

<style lang="scss" scoped>
.vue-map-container {
  height: 450px;
  max-width: 992px;
  width: 100%;
}
</style>
