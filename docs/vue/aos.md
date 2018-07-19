---
title: How to Use AOS Library in a Vue Project
meta:
  - name: description
    content: 
---

# {{ $page.title }}

::: tip First visit?
Learn the project structure of my tutorials [here](./).
:::

[DEMO](https://vuedemo.netlify.com/aos)

First, let's install [AOS](https://github.com/michalsnik/aos) and serve the project.

```bash{2}
cd vue-demo
npm i aos@next --save
npm run serve
```

Then, we need to register and initialize AOS in `src/main.js`.

<<< @/vue-demo/src/main.js{6,7,12,13,14}

In this example, I also passed an optional [setting](https://github.com/michalsnik/aos#1-initialize-aos) to disable AOS on the phone.

Now we can start setting [animations](https://github.com/michalsnik/aos#animations) using `data-aos` attribute. We can also adjust the behaviour with the `data-aos-*` attributes. Here is the code in `src/views/aos.vue`.

<<< @/vue-demo/src/views/aos.vue{3,6,7,8,31,32,34,37,38,41,42}

A quick note about the attributes above:

- `delay` delays the animation start time. Both this and `duration` [accept values](https://github.com/michalsnik/aos#setting-duration-delay) from 50 to 3000, with step 50ms.
- `once` limits the animation to fire only once.
- `duration` sets how long the animation lasts.
- `easing` is for changing the transition function.
- `anchor` makes another element triggers the animation.
