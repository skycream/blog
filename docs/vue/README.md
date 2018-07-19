---
title: Vue Blog
meta:
  - name: description
    content: 
---

# {{ $page.title }}

You can find tutorials and walkthroughs related to [Vue](https://vuejs.org/) here.

I start the project with `vue create vue-demo`.

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

<<< @/vue-demo/package.json{13,14,15,18,19,20,21,22,23,24,25}

Finally, let's launch the project with `npm run serve`.

::: warning
You will find `src/main.js` contains more code than you need. I highlight the relevant parts though. I place everything inside `vue-demo` because I do not want to deal with a lot of small repositories.
:::

If you would like to request a tutorial, have an idea for a walkthrough, or have any suggestions to make this blog better, feel free to [tell me](mailto:yasmin@yasminzy.com) about it.
