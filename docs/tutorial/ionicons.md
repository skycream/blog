---
title: How to Use Ionicons in a Vue/Nuxt Project
meta:
  - name: description
    content: Steps to use Ionicons in a Vue/Nuxt project.
---

# {{ $page.title }}

<start-tutorial demo="ionicons" />

## Installation

### Vue

Include [Ionicons](https://github.com/ionic-team/ionicons) in `public/index.html`.

<<< vue-demo/public/index.html{20}

### Nuxt

Include [Ionicons](https://github.com/ionic-team/ionicons) in `nuxt.config.js`.

<<< nuxt-demo/nuxt.config.js{13}

## Usage

To use the icon, insert the `ion-icon` web component to your template. Specify the icon in the `name` attribute. For example, to insert a heart icon write `<ion-icon name="heart" />`.

In `src/views/ionicons.vue` and `pages/ionicons.vue`:

<<< vue-demo/src/views/ionicons.vue{21}

`src/assets/ionicons.js` and `assets/ionicons.js` contain the icons name.

```js
const appIcons = [
  "add-circle-outline",
  "add-circle",
  "add"
  // and so on
];

const logos = [
  "logo-android",
  "logo-angular",
  "logo-apple"
  // and so on
];

export { appIcons, logos };
```

I use another file for the demo because I want to include every icon. You may not need all that so only include what you need.