---
title: How to Use Prism in a Vue/Nuxt Project
meta:
  - name: description
    content: Steps to use Prism in a Vue/Nuxt project.
---

# {{ $page.title }}

<start-tutorial demo="prism"/>

## Installation

### Vue

First, install [Prism](https://github.com/PrismJS/prism) and [vue-prism-component](https://github.com/egoist/vue-prism-component).

```bash{2}
cd vue-demo
npm i -S prismjs vue-prism-component
```

In `src/main.js`:

<<< @/vue-demo/src/main.js{20-27}

In this example, I use the funky theme. Here are the available themes:

- prism-coy
- prism-dark
- prism-funky
- prism-okaidia
- prism-solarizedlight
- prism-tomorrow
- prism-twilight
- prism

I also add an scss [component](https://prismjs.com/index.html#languages-list). Markup, CSS, JavaScript, and C-like are supported by default so we do not need to import them.

Prism supports some [plugins](https://prismjs.com/index.html#plugins). I use [autolinker](https://prismjs.com/plugins/autolinker) here to make the link in the code works.

### Nuxt

First, install [Prism](https://github.com/PrismJS/prism) and [vue-prism-component](https://github.com/egoist/vue-prism-component).

```bash{2}
cd nuxt-demo
npm i -S prismjs vue-prism-component
```

In `nuxt.config.js`:

<<< @/nuxt-demo/nuxt.config.js{32}

In `plugins/prism.js`:

<<< @/nuxt-demo/plugins/prism.js

## Usage

Now we can use `prism` component. Specify the language in the `language` attribute. The default is markup.

In `src/views/prism.vue` and `pages/prism.vue`:

<<< @/vue-demo/src/views/prism.vue{6,9-12,15-21,29-32}
