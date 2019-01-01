---
title: Tutorial
meta:
  - name: description
    content: How I start the Vue and Nuxt tutorials.
---

# {{ $page.title }}

I write [Vue](https://vuejs.org/) and [Nuxt](https://nuxtjs.org/) tutorials. I do not start each tutorial from scratch, so I will show you how I set them up here.

::: warning
You will find `src/main.js` and `nuxt.config.js` contain more code than you need. I highlight the relevant parts though. I place everything inside `vue-demo` and `nuxt-demo` so I do not have to take care a lot of repositories.
:::

## Vue

The demo projects using Vue are available in [vue-demo](https://github.com/yasminzy/blog/tree/master/vue-demo). The project scaffolding follows `vue create vue-demo`.

I also install [Picnic CSS](https://github.com/franciscop/picnic). Most of the tutorials here will use this. The only exceptions are the ones about using other CSS library.

Here is the current `package.json`.

<<< vue-demo/package.json

Finally, let's launch the project with `npm run serve`.

## Nuxt

The demo projects using Nuxt are available in [nuxt-demo](https://github.com/yasminzy/blog/tree/master/nuxt-demo). The project scaffolding follows `npx create-nuxt-app`.

Like the Vue tutorials, I also install [Picnic CSS](https://github.com/franciscop/picnic) here.

Here is the current `package.json`.

<<< nuxt-demo/package.json

Finally, let's launch the project with `npm run dev`.

---

If you would like to request a tutorial or have a suggestion to make this blog better, feel free to [tell me](mailto:yasmin@yasminzy.com) about it.
