---
title: Blog Vue
meta:
  - name: description
    content: 
---

# {{ $page.title }}

Kamu bisa menemukan tutorial dan walkthrough terkait [Vue](https://vuejs.org/) disini.

Struktur awal proyek untuk tutorial-tutorial ini adalah:

`vue create vue-demo`

- **Vue CLI v3.0.0-rc.5**
- Please pick a preset: **Manually select features**
- Check the features needed for your project: **Babel, Router, Vuex, CSS Pre-processors, Linter**
- Pick a CSS pre-processor (PostCSS, Autoprefixer and CSS Modules are supported by default): **SCSS/SASS**
- Pick a linter / formatter config: **Prettier**
- Pick additional lint features: **Lint on save, Lint and fix on commit**
- Where do you prefer placing config for Babel, PostCSS, ESLint, etc.? **In dedicated config files**
- Save this as a preset for future projects? **No**

Tidak semua dari CLI adalah yang terbaru, contohnya `node-sass` dan `sass-loader` jadi saya perbarui mereka sendiri.

Saya juga menginstal [Picnic CSS](https://github.com/franciscop/picnic). Sebagian besar tutorial disini akan menggunakan ini. Pengecualian hanya berlaku untuk tutorial tentang cara menggunakan CSS library yang lain.

Ini adalah `package.json` sekarang.

<<< @/vue-demo/package.json

Nah, sekarang ayo kita jalankan proyek ini dengan `npm run serve`.

::: warning PERINGATAN
Kamu akan melihat `src/main.js` berisi lebih banyak kode dari yang kamu butuhkan. Meskipun begitu, saya menyoroti bagian-bagian yang relevan. Saya meletakkan semuanya dalam `vue-demo` karena saya tidak ingin mengurus banyak repositories kecil.
:::

Kalau kamu ingin meminta tutorial tertentu, punya ide untuk walkthrough, atau punya saran untuk membuat blog ini lebih baik, jangan ragu untuk [memberitahu saya](mailto:yasmin@yasminzy.com) tentang itu.
