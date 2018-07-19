---
title: Blog Nuxt
meta:
  - name: description
    content: 
---

# {{ $page.title }}

Kamu bisa menemukan tutorial dan walkthrough terkait [Nuxt](https://nuxtjs.org/) disini.

Saya memulai proyek dengan `vue init nuxt-community/starter-template nuxt-demo`.

Sekarang, ayo kita instal dependencies-nya.

```bash{2}
cd nuxt-demo
npm i
```

CLI-nya tidak menggunakan packages terbaru, jadi saya perbarui mereka sendiri.

Saya juga menginstal [Picnic CSS](https://github.com/franciscop/picnic). Sebagian besar tutorial disini akan menggunakan ini. Pengecualian hanya berlaku untuk tutorial tentang cara menggunakan CSS library yang lain. Untuk membuatnya custom, saya install `node-sass` dan `sass-loader` juga.

Ini adalah `package.json` sekarang.

<<< @/nuxt-demo/package.json{17,21,22,23,24,25}

Nah, sekarang ayo kita jalankan proyek ini dengan `npm run dev`.

::: warning PERINGATAN
Kamu akan melihat `nuxt.config.js` berisi lebih banyak kode dari yang kamu butuhkan. Meskipun begitu, saya menyoroti bagian-bagian yang relevan. Saya meletakkan semuanya dalam `nuxt-demo` karena saya tidak ingin mengurus banyak repositories kecil.
:::

Kalau kamu ingin meminta tutorial tertentu, punya ide untuk dibuat walkthrough-nya, atau punya saran untuk membuat blog ini lebih baik, jangan ragu untuk [memberitahu saya](mailto:yasmin@yasminzy.com) tentang itu.
