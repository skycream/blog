---
title: How to Integrate Prettier with ESLint in a Vue/Nuxt Project
meta:
  - name: description
    content: Steps to use Prettier with ESLint in a Vue/Nuxt project.
---

# {{ $page.title }}

<start-tutorial/>

## Installation

### Vue

:::tip INFO
You do not need to do this if you started your project with Vue CLI and picked Prettier as the formatter.
:::

First, install [eslint-config-prettier](https://github.com/vuejs/vue-cli/tree/dev/packages/%40vue/eslint-config-prettier).

```bash{2}
cd vue-demo
npm i -D @vue/eslint-config-prettier
```

In `.eslintrc.js`:

<<< @/vue-demo/.eslintrc.js{6}

### Nuxt

First, install [eslint-plugin-prettier](https://github.com/prettier/eslint-plugin-prettier) and [eslint-config-prettier](https://github.com/prettier/eslint-config-prettier).

```bash{2}
cd nuxt-demo
npm i -D eslint-plugin-prettier eslint-config-prettier
```

In `.eslintrc.js`:

<<< @/nuxt-demo/.eslintrc.js{14}

## Usage

Run `npm run serve` or `npm run dev`. You will see Prettier warning if your files break any of its rules.

You can use [Prettier extension](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) for VS Code to make formatting easier.

First, install it with `ext install esbenp.prettier-vscode` in Quick Open (Ctrl+P).

Then, in your settings (Ctrl+,) write `"editor.formatOnSave": true`.

Now Prettier will format your file when you save it.
