<template>
<div>
  <h1>Ionicons Demo</h1>

  <div class="grid">
    <table v-for="(item, index) in ionicons"
      v-bind:key="index">
      <thead>
        <tr>
          <th>{{ item.name }}</th>
          <th>Icon</th>
        </tr>
      </thead>
      
      <tbody>
        <tr v-for="(item, index) in item.icons"
          v-bind:key="index">
          <td>{{ item }}</td>
          <td><ion-icon v-bind:name="item"/></td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
</template>

<script>
import { appIcons, logos } from "@/assets/ionicons";

export default {
  data() {
    return {
      ionicons: [
        {
          name: "App icons",
          icons: appIcons
        },
        {
          name: "Logos",
          icons: logos
        }
      ]
    };
  }
};
</script>

<style lang="scss" scoped>
.grid {
  display: grid;
  grid-row-gap: 2rem;

  @media (min-width: 768px) {
    grid-template-columns: 1fr 1fr;
    grid-column-gap: 2.5rem;
  }
}

th,
td:nth-child(2) {
  text-align: center;
}
</style>
