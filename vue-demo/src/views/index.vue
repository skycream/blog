<template>
  <div>
    <h1>Vue Demo</h1>

    <ul>
      <li v-for="(item, index) in projects" v-bind:key="index">
        <router-link v-bind:to="urlize(item)">{{ item }}</router-link>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      projects: ["AOS", "Chart", "Google Maps", "Ionicons", "Prism"]
    };
  },
  methods: {
    urlize(input) {
      if (input) {
        return (
          "/" +
          input
            .toLowerCase()
            .replace(/\s/g, "-")
            .replace(/[^-a-z0-9A-Z_]/g, "")
        );
      }
    }
  }
};
</script>
