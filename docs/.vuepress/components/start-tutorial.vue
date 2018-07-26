<template>
<div>
  <blockquote>
    <p v-if="lang == 'id'"><a class="router-link-active" href="./">Pertama kali kesini? 😁</a></p>
    <p v-else><a class="router-link-active" href="./">First visit? 😁</a></p>
  </blockquote>

  <ul v-show="demo">
    <li v-for="(item, index) in links"
      v-bind:key="index">
      <a target="_blank" rel="noopener noreferrer"
        v-bind:href="item.url + demo">
        {{ item.label }}
        <external-link-svg/>
      </a>
    </li>
  </ul>
</div>
</template>

<script>
import ExternalLinkSvg from "./external-link-svg";

export default {
  components: {
    ExternalLinkSvg
  },
  props: {
    lang: {
      type: String,
      default: "en"
    },
    demo: {
      type: String,
      default: ""
    }
  },
  data() {
    return {
      links: [
        {
          label: "Vue demo",
          url: "https://vuedemo.netlify.com/"
        },
        {
          label: "Nuxt demo",
          url: "https://nuxtdemo.netlify.com/"
        }
      ]
    };
  }
};
</script>