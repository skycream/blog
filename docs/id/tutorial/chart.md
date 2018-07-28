---
title: Bagaimana Cara Menggunakan Vue Charts dalam Proyek Vue/Nuxt
meta:
  - name: description
    content: Langkah menggunakan Vue Charts dalam proyek Vue/Nuxt (demo grafik garis, bar, dan donat).
---

# {{ $page.title }}

<start-tutorial demo="chart" lang="id"/>

## Instalasi

### Vue

Pertama, instal [Vue Charts](https://github.com/hchstera/vue-charts).

```bash{2}
cd vue-demo
npm i -S chart.js hchs-vue-charts
```

Dalam `src/main.js`:

<<< @/vue-demo/src/main.js{11-13}

### Nuxt

First, install [Vue Charts](https://github.com/hchstera/vue-charts).

```bash{2}
cd nuxt-demo
npm i -S chart.js hchs-vue-charts
```

Dalam `nuxt.config.js`:

<<< @/nuxt-demo/nuxt.config.js{34}

Dalam `plugins/chart.js`:

<<< @/nuxt-demo/plugins/chart.js

Dalam `plugins/hchs-vue-charts.js`:

<<< @/nuxt-demo/plugins/hchs-vue-charts.js

## Penggunaan

Saya ingin menggunakan tiga macam grafik. Saya bagi mereka menjadi komponen-komponen agar kodenya lebih mudah dibaca.

Dalam `src/views/chart.vue` dan `pages/chart.vue`:

<<< @/vue-demo/src/views/chart.vue

### Garis

Dalam `src/components/chart-line.vue`:

<<< @/vue-demo/src/components/chart-line.vue{7-13,38-50}

- `beginzero` membuat grafik mulai dari nol jika di-set `true`.
- `labels` mengatur label di sumbu-x.
- `datalabel` adalah untuk nama data.
- `data` menerima array data.
- `backgroundcolor` mengubah warna latar.
- `bordercolor` mengatur warna border.
- `bind` membuat grafik [re-render](http://vue-charts.hchspersonal.tk/databinding) ketika ada perubahan data, jika di-set `true`.

### Bar

Dalam `src/components/chart-bar.vue`:

<<< @/vue-demo/src/components/chart-bar.vue{6-17,26-39}

Untuk memasukkan lebih dari satu grafik, dalam contoh ini bar charts, tambahkan `canvas`.

### Donat

Dalam `src/components/chart-doughnut.vue`:

<<< @/vue-demo/src/components/chart-doughnut.vue{6-9,18-26}

- `datasets` berguna untuk mengganti beberapa hal sekaligus.
- `hoverBackgroundColor` adalah untuk mengatur latar warna ketika kita hover over grafik.

Disini ada [isu](https://github.com/hchstera/vue-charts/issues/33) jadi kita perlu menambahkan objek kosong di `option` juga.

Komponen-komponen untuk Nuxt hampir identik dengan komponen diatas. Bedanya hanya `div` setelah `template` ada di dalam komponen `no-ssr`. Seperti ini:

```html{2,6}
<template>
<no-ssr>
  <div>
    <!-- content -->
  </div>
</no-ssr>
</template>
```
