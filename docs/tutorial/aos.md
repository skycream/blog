---
title: How to Use AOS Library in a Vue/Nuxt Project
meta:
  - name: description
    content: 
---

# {{ $page.title }}

<start-tutorial topic="aos"/>

## Installation

### Vue

First, install [AOS](https://github.com/michalsnik/aos).

```bash{2}
cd vue-demo
npm i aos@next --save
```

In `src/main.js`:

<<< @/vue-demo/src/main.js{8,9,19-21}

In this example, I also passed an optional [setting](https://github.com/michalsnik/aos#1-initialize-aos) to disable AOS on the phone.

### Nuxt

First, install [AOS](https://github.com/michalsnik/aos).

```bash{2}
cd nuxt-demo
npm i aos@next --save
```

In `nuxt.config.js`:

<<< @/nuxt-demo/nuxt.config.js{27,29,30}

In `plugins/aos.js`:

<<< @/nuxt-demo/plugins/aos.js

Like before, I also passed an optional [setting](https://github.com/michalsnik/aos#1-initialize-aos) to disable AOS on the phone.

## Usage

Now we can start setting [animations](https://github.com/michalsnik/aos#animations) using `data-aos` attribute. We can also adjust the behaviour with the `data-aos-*` attributes.

In `src/views/aos.vue` and `pages/aos.vue`:

<<< @/vue-demo/src/views/aos.vue{3,6-8,31,32,34,37,38,41,42}

A quick note about the attributes above:

- `delay` delays the animation start time. Both this and `duration` [accept values](https://github.com/michalsnik/aos#setting-duration-delay) from 50 to 3000, with step 50ms.
- `once` limits the animation to fire only once.
- `duration` sets how long the animation lasts.
- `easing` is for changing the transition function.
- `anchor` makes another element triggers the animation.