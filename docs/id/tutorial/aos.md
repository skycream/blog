---
title: Bagaimana Cara Menggunakan AOS Library dalam Proyek Vue/Nuxt
meta:
  - name: description
    content: Langkah penggunaan Animation on Scroll (AOS) library dalam proyek Vue/Nuxt.
---

# {{ $page.title }}

<start-tutorial demo="aos" lang="id"/>

## Instalasi

### Vue

Pertama, instal [AOS](https://github.com/michalsnik/aos).

```bash{2}
cd vue-demo
npm i -S aos@next
```

Dalam `src/main.js`:

<<< @/vue-demo/src/main.js{8,9,32-34}

Pada contoh ini, saya juga memasukkan [setting](https://github.com/michalsnik/aos#1-initialize-aos) opsional untuk menonaktifkan AOS di ponsel.

### Nuxt

Pertama, instal [AOS](https://github.com/michalsnik/aos).

```bash{2}
cd nuxt-demo
npm i -S aos@next
```

Dalam `nuxt.config.js`:

<<< @/nuxt-demo/nuxt.config.js{33}

Dalam `plugins/aos.js`:

<<< @/nuxt-demo/plugins/aos.js

Seperti sebelummya, saya juga memasukkan [setting](https://github.com/michalsnik/aos#1-initialize-aos) opsional untuk menonaktifkan AOS di ponsel.

## Penggunaan

Sekarang kita bisa mulai mengatur [animasi](https://github.com/michalsnik/aos#animations) dengan atribut `data-aos`. Kita ujga bisa mengatur perilakunya dengan atribut `data-aos-*`.

Dalam `src/views/aos.vue` dan `pages/aos.vue`:

<<< @/vue-demo/src/views/aos.vue{3,6-8,31,32,34,37,38,41,42}

- `delay` menunda waktu mulai animasi. Ini dan `duration` [menerima nilai](https://github.com/michalsnik/aos#setting-duration-delay) mulai dari 50 sampai 3000, dengan langkah 50ms.
- `once` membatasi jumlah animasi berjalan menjadi hanya sekali.
- `duration` mengatur berapa lama animasi berlangsung.
- `easing` adalah untuk mengatur fungsi transisi.
- `anchor` membuat elemen lain menjadi pemicu mulainya animasi.
