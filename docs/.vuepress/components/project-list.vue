<template>
<ul>
  <li
    v-for="(item, index) in projects"
    v-bind:key="index">
    <a target="_blank"
      v-bind:href="item.url">{{ item.title }}
      <img
        v-bind:src="'/img/' + item.img"
        v-bind:alt="item.title"/>
    </a>

    <div>
      <h2>
        <a target="_blank"
          v-bind:href="item.url">
          {{ item.title }}
        </a>
      </h2>
      
      <p v-if="lang == 'id'">{{ item.description.id }}</p>
      <p v-else>{{ item.description.en }}</p>
    </div>
  </li>
</ul>
</template>

<script>
import { projects } from "../../data.js";

export default {
  props: {
    lang: {
      type: String,
      default: "en"
    }
  },
  data() {
    return {
      projects
    };
  }
};
</script>

<style lang="stylus" scoped>
ul {
  list-style-type: none;
  padding-left: 0;
  display: grid;
  grid-row-gap: 2rem;

  @media (min-width: 576px) {
    grid-template-columns: 1fr 1fr;
    grid-column-gap: 2.5rem;
  }

  @media (min-width: 1200px) {
    grid-template-columns: repeat(3, 1fr);
    grid-column-gap: 5rem;
  }
}

a {
  cursor: pointer;
}
</style>