---
title: How to Use Vue Charts in a Vue/Nuxt Project
meta:
  - name: description
    content: Steps to use Vue Charts in a Vue/Nuxt project (line, bar, and doughnut charts demo).
---

# {{ $page.title }}

<start-tutorial demo="chart" />

## Installation

### Vue

First, install [Vue Charts](https://github.com/hchstera/vue-charts).

```bash{2}
cd vue-demo
npm i -S chart.js hchs-vue-charts
```

In `src/main.js`:

<<< vue-demo/src/main.js{11-13}

### Nuxt

First, install [Vue Charts](https://github.com/hchstera/vue-charts).

```bash{2}
cd nuxt-demo
npm i -S chart.js hchs-vue-charts
```

In `nuxt.config.js`:

<<< nuxt-demo/nuxt.config.js{20}

In `plugins/chart.js`:

<<< nuxt-demo/plugins/chart.js

## Usage

I want to use three kinds of charts. I split them into components to make the code easier to read.

In `src/views/chart.vue` and `pages/chart.vue`:

<<< vue-demo/src/views/chart.vue

### Line

In `src/components/chart-line.vue`:

<<< vue-demo/src/components/chart-line.vue{7-15,36-47}

- `beginzero` makes the chart starts from zero if set to `true`.
- `labels` sets the x-axis labels.
- `datalabel` is for the data name.
- `data` accepts an array of data.
- `backgroundcolor` changes the background color.
- `bordercolor` specifies the border color.
- `bind` makes the chart [re-render](http://vue-charts.hchspersonal.tk/databinding) when the data changes, if set to `true`.

### Bar

In `src/components/chart-bar.vue`:

<<< vue-demo/src/components/chart-bar.vue{6-19,28-41}

To add many charts, bar charts in this case, add a `canvas`.

### Doughnut

In `src/components/chart-doughnut.vue`:

<<< vue-demo/src/components/chart-doughnut.vue{6-11,20-28}

- `datasets` is useful for changing many things at once.
- `hoverBackgroundColor` is for setting the background color when we hover over the chart.

There is also this [issue](https://github.com/hchstera/vue-charts/issues/33) so we need to add that empty object for the `option` as well.

The components for Nuxt are almost identical with the above components. The only difference is the `div` after `template` is wrapped in a `vue-no-ssr` component. Like this:

```html{2,6}
<template>
<vue-no-ssr>
  <div>
    <!-- content -->
  </div>
</vue-no-ssr>
</template>
```
