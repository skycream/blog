---
title: Tutorial
meta:
  - name: description
    content: 
---

# {{ $page.title }}

I write [Vue](https://vuejs.org/) and [Nuxt](https://nuxtjs.org/) tutorials. I do not start each tutorial from scratch, so I will show you how I set them up here.

::: warning
You will find `src/main.js` and `nuxt.config.js` contain more code than you need. I highlight the relevant parts though. I place everything inside `vue-demo` and `nuxt-demo` because I do not want to take care lots of repositories.
:::

## Vue

The demo projects using Vue are available in [vue-demo](https://github.com/yasminzy/blog/tree/master/vue-demo). I start it with `vue create vue-demo`.

- **Vue CLI v3.0.0-rc.5**
- Please pick a preset: **Manually select features**
- Check the features needed for your project: **Babel, Router, Vuex, CSS Pre-processors, Linter**
- Pick a CSS pre-processor (PostCSS, Autoprefixer and CSS Modules are supported by default): **SCSS/SASS**
- Pick a linter / formatter config: **Prettier**
- Pick additional lint features: **Lint on save, Lint and fix on commit**
- Where do you prefer placing config for Babel, PostCSS, ESLint, etc.? **In dedicated config files**
- Save this as a preset for future projects? **No**

Not everything from the CLI is the latest, for example `node-sass` and `sass-loader` so I update them myself.

I also install [Picnic CSS](https://github.com/franciscop/picnic). Most of the tutorials here will use this. The only exceptions are the ones about using other CSS library.

Here is the current `package.json`.

<<< @/vue-demo/package.json{13-15,17,20-27}

Finally, let's launch the project with `npm run serve`.

## Nuxt

The demo projects using Nuxt are available in [nuxt-demo](https://github.com/yasminzy/blog/tree/master/nuxt-demo). I start it with:

```bash{2}
vue init nuxt-community/starter-template nuxt-demo
cd nuxt-demo
npm i
```

The CLI does not use the latest packages, so I updated them myself.

Like the Vue tutorials, I also install [Picnic CSS](https://github.com/franciscop/picnic) here. To customize it, I install `node-sass` and `sass-loader` as well.

Here is the current `package.json`.

<<< @/nuxt-demo/package.json{18,19,23-29}

Finally, let's launch the project with `npm run dev`.

If you would like to request a tutorial or have a suggestion to make this blog better, feel free to [tell me](mailto:yasmin@yasminzy.com) about it.
