---
title: Nuxt Blog
meta:
  - name: description
    content: 
---

# {{ $page.title }}

You can find tutorials and walkthroughs related to [Nuxt](https://nuxtjs.org/) here.

I start the project with `vue init nuxt-community/starter-template nuxt-demo`.

Now, let's install the dependencies.

```bash{2}
cd nuxt-demo
npm i
```

The CLI does not use the latest packages, so I updated them myself.

I also install [Picnic CSS](https://github.com/franciscop/picnic). Most of the tutorials here will use this. The only exceptions are the ones about using other CSS library. To customize it, I install `node-sass` and `sass-loader` as well.

Here is the current `package.json`.

<<< @/nuxt-demo/package.json{17,21,22,23,24,25}

Finally, let's launch the project with `npm run dev`.

::: warning
You will find `nuxt.config.js` contains more code than you need. I highlight the relevant parts though. I place everything inside `nuxt-demo` because I do not want to deal with a lot of small repositories.
:::

If you would like to request a tutorial, have an idea for a walkthrough, or have any suggestions to make this blog better, feel free to [tell me](mailto:yasmin@yasminzy.com) about it.
