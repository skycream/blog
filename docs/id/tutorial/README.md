---
title: Tutorial
meta:
  - name: description
    content: Bagaimana saya memulai tutorial-tutorial Vue dan Nuxt.
---

# {{ $page.title }}

Saya menulis tutorial tentang [Vue](https://vuejs.org/) dan [Nuxt](https://nuxtjs.org/). Saya tidak memulai tiap tutorial from scratch, jadi berikut adalah awal proyeknya.

::: warning PERINGATAN
Kamu akan melihat `src/main.js` dan `nuxt.config.js` berisi lebih banyak kode dari yang dibutuhkan. Meski begitu, saya menghighlight bagian-bagian yang relevan. Saya memasukkan semuanya dalam `vue-demo` dan `nuxt-demo` jadi saya tidak perlu mengurus banyak repositories.
:::

## Vue

Proyek demo yang menggunakan Vue ada dalam [vue-demo](https://github.com/yasminzy/blog/tree/master/vue-demo). Saya mulai dengan `vue create vue-demo`.

- **Vue CLI v3.0.0-rc.5**
- Please pick a preset: **Manually select features**
- Check the features needed for your project: **Babel, Router, Vuex, CSS Pre-processors, Linter**
- Pick a CSS pre-processor (PostCSS, Autoprefixer and CSS Modules are supported by default): **SCSS/SASS**
- Pick a linter / formatter config: **Prettier**
- Pick additional lint features: **Lint on save, Lint and fix on commit**
- Where do you prefer placing config for Babel, PostCSS, ESLint, etc.? **In dedicated config files**
- Save this as a preset for future projects? **No**

Tidak semua dari CLI adalah package terbaru, contohnya `node-sass` dan `sass-loader`. Karena itu saya perlu memperbarui mereka sendiri.

Saya juga menginstal [Picnic CSS](https://github.com/franciscop/picnic). Kebanyakan tutorial disini akan menggunakan ini. Pengecualian hanya ada untuk tutorial tentang cara menggunakan CSS library lainnya.

Ini adalah `package.json` sekarang.

<<< @/vue-demo/package.json

Nah, sekarang ayo kita jalankan proyek dengan `npm run serve`.

## Nuxt

Proyek demo yang menggunakan Nuxt ada dalam [nuxt-demo](https://github.com/yasminzy/blog/tree/master/nuxt-demo). Saya mulai dengan:

```bash
vue init nuxt-community/starter-template nuxt-demo
cd nuxt-demo
npm i
```

CLI ini belum menggunakan packages terbaru, jadi saya perbarui mereka sendiri.

Seperti tutorial untuk Vue, saya juga menginstal [Picnic CSS](https://github.com/franciscop/picnic) disini. Untuk membuatnya custom, saya juga menginstal `node-sass` dan `sass-loader`.

Ini adalah `package.json` sekarang.

<<< @/nuxt-demo/package.json

Nah, sekarang ayo kita jalankan proyek dengan `npm run dev`.

Kalau kamu mau meminta tutorial tertentu atau punya saran untuk membuat blog ini lebih baik, jangan ragu untuk [memberitahu saya](mailto:yasmin@yasminzy.com) tentang itu.
