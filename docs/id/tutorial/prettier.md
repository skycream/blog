---
title: Bagaimana Cara Menggunakan Prettier dengan ESLint dalam Proyek Vue/Nuxt
meta:
  - name: description
    content: Langkah penggunaan Prettier dengan ESLint dalam proyek Vue/Nuxt.
---

# {{ $page.title }}

<start-tutorial lang="id" />

## Instalasi

### Vue

:::tip INFO
Kamu tidak perlu mengikuti ini kalau kamu memulai proyekmu dengan Vue CLI dan memilih Prettier sebagai formatter.
:::

Pertama, instal [eslint-config-prettier](https://github.com/vuejs/vue-cli/tree/dev/packages/%40vue/eslint-config-prettier).

```bash{2}
cd vue-demo
npm i -D @vue/eslint-config-prettier
```

Dalam `.eslintrc.js`:

<<< vue-demo/.eslintrc.js{6}

### Nuxt

Pertama, instal [eslint-plugin-prettier](https://github.com/prettier/eslint-plugin-prettier) dan [eslint-config-prettier](https://github.com/prettier/eslint-config-prettier).

```bash{2}
cd nuxt-demo
npm i -D eslint-plugin-prettier eslint-config-prettier
```

Dalam `.eslintrc.js`:

<<< nuxt-demo/.eslintrc.js{10-11}

## Penggunaan

Jalankan `npm run serve` atau `npm run dev`. Kamu akan melihat peringatan dari Prettier kalau ada file yang tidak sesuai aturannya.

Kamu bisa menggunakan [ekstensi Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) untuk VS Code untuk membuat formatting lebih mudah.

Pertama, instal ekstensinya dengan `ext install esbenp.prettier-vscode` di Quick Open (Ctrl+P).

Kemudian, di pengaturan (Ctrl+,) tulis `"editor.formatOnSave": true`.

Sekarang Prettier akan memformat file-mu ketika kamu menyimpannya.
