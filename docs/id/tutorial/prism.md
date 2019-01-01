---
title: Bagaimana Cara Menggunakan Prism dalam Proyek Vue/Nuxt
meta:
  - name: description
    content: Langkah Penggunaan Prism dalam Proyek  Vue/Nuxt.
---

# {{ $page.title }}

<start-tutorial demo="prism" lang="id" />

## Instalasi

### Vue

Pertama, instal [Prism](https://github.com/PrismJS/prism) dan [vue-prism-component](https://github.com/egoist/vue-prism-component).

```bash{2}
cd vue-demo
npm i -S prismjs vue-prism-component
```

Dalam `src/main.js`:

<<< vue-demo/src/main.js{20-26}

Pada contoh ini, saya menggunakan tema funky. Berikut adalah tema yang tersedia:

- prism-coy
- prism-dark
- prism-funky
- prism-okaidia
- prism-solarizedlight
- prism-tomorrow
- prism-twilight
- prism

Saya juga menambahkan [komponen](https://prismjs.com/index.html#languages-list) scss. Markup, CSS, JavaScript, dan C-like didukung secara default jadi kita tidak perlu mengimpor mereka.

Prism mendukung beberapa [plugins](https://prismjs.com/index.html#plugins). Saya menggunakan [autolinker](https://prismjs.com/plugins/autolinker) disini untuk membuat link dalam kode bekerja.

### Nuxt

Pertama, instal [Prism](https://github.com/PrismJS/prism) dan [vue-prism-component](https://github.com/egoist/vue-prism-component).

```bash{2}
cd nuxt-demo
npm i -S prismjs vue-prism-component
```

Dalam `nuxt.config.js`:

<<< nuxt-demo/nuxt.config.js{18}

Dalam `plugins/prism.js`:

<<< nuxt-demo/plugins/prism.js

## Penggunaan

Sekarang kita bisa menggunakan komponen `prism`. Masukkan bahasa di atribut `language`. Default-nya adalah markup.

Dalam `src/views/prism.vue` dan `pages/prism.vue`:

<<< vue-demo/src/views/prism.vue{6,9-12,15-21,29-32}
