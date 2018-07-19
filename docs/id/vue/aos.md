---
title: Bagaimana Cara Menggunakan AOS Library dalam Proyek Vue
meta:
  - name: description
    content: 
---

# {{ $page.title }}

::: tip Pertama kali kesini?
Lihat struktur proyek tutorial saya [disini](./).
:::

[DEMO](https://vuedemo.netlify.com/aos)

Pertama-tama, ayo instal [AOS](https://github.com/michalsnik/aos) dan jalankan proyek ini.

```bash{2}
cd vue-demo
npm i aos@next --save
npm run serve
```

Kemudian, kita perlu mendaftarkan dan menginisialisasi AOS di `src/main.js`.

<<< @/vue-demo/src/main.js{6,7,12,13,14}

Pada contoh ini, saya juga masukkan [setting](https://github.com/michalsnik/aos#1-initialize-aos) opsional untuk menonaktifkan AOS di ponsel.

Sekarang kita bisa mulai mengatur [animasi](https://github.com/michalsnik/aos#animations) mengunakan atribut `data-aos`. Kita juga bisa mengatur perilaku animasi dengan atribut `data-aos-*`. Berikut adalah kode dalam `src/views/aos.vue`.

<<< @/vue-demo/src/views/aos.vue{3,6,7,8,31,32,34,37,38,41,42}

Catatan singkat tentang atribut-atribut diatas:

- `delay` menunda waktu mulai animasi. Ini dan `duration` sama-sama [menerima nilai](https://github.com/michalsnik/aos#setting-duration-delay) dari 50 sampai 3000, dengan langkah 50ms.
- `once` membatasi animasi untuk berjalan hanya sekali.
- `duration` mengatur berapa lama animasi berjalan.
- `easing` adalah untuk mengganti fungsi transisi yang digunakan.
- `anchor` membuat elemen lain menjadi pemicu animasi.
