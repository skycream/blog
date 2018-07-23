---
title: How to Embed Google Maps in a Vue/Nuxt Project
meta:
  - name: description
    content: 
---

# {{ $page.title }}

<start-tutorial topic="google-maps"/>

## Get API Key

First, get an API key from the [Google Maps Platform](https://cloud.google.com/maps-platform/). Click **Get Started**.

1.  Pick a product ![Pick product](../img/gmaps-1-pick-product.png)

2.  Select a project ![Select project](../img/gmaps-2-select-project.png)

3.  Create a billing account ![Create billing account](../img/gmaps-3-create-billing-account.png)

4.  Accept the terms of service ![Accept terms](../img/gmaps-4-accept-terms.png)

5.  Create a payment profile ![Create payment profile](../img/gmaps-5-create-payment-profile.png)

6.  Enable the API ![Enable API](../img/gmaps-6-enable-api.png)

7.  Get the API key ![Get API key](../img/gmaps-7-get-api-key.png)

## Installation

### Vue

Now, install [vue-google-maps](https://github.com/xkjyeah/vue-google-maps) and [dotenv](https://github.com/motdotla/dotenv).

```bash{2}
cd vue-demo
npm i vue2-google-maps dotenv
```

In `src/main.js`:

<<< @/vue-demo/src/main.js{1,11-14}

After that, create a file named `.env` in the project root and paste your API key. For example:

```env
VUE_APP_GOOGLE_MAPS_API_KEY=ABcdEfGhIjklmNOpqrsTUvWXyzAbcD1EfGhiJKl
```

### Nuxt

Now, install [vue-google-maps](https://github.com/xkjyeah/vue-google-maps) and [@nuxtjs/dotenv](https://github.com/nuxt-community/dotenv-module).

```bash{2}
cd nuxt-demo
npm i vue2-google-maps @nuxtjs/dotenv
```

In `nuxt.config.js`:

<<< @/nuxt-demo/nuxt.config.js{27,29,30}

In `plugins/vue2-google-maps.js`:

<<< @/nuxt-demo/plugins/vue2-google-maps.js

After that, create a file named `.env` in the project root and paste your API key. For example:

```env
VUE_APP_GOOGLE_MAPS_API_KEY=ABcdEfGhIjklmNOpqrsTUvWXyzAbcD1EfGhiJKl
```

## Usage

Now we can start embedding Google Maps.

In `src/views/google-maps.vue` and `pages/google-maps.vue`:

<<< @/vue-demo/src/views/google-maps.vue{5-14,22-27}

We can specify the center of the map with `center`. To make the map zoomed in more, increase the value of `zoom`.

There are four map types we can use for `map-type-id`:

- roadmap
- hybrid
- satellite
- terrain

`gmap-marker` is one of the components supported by `vue-google-maps`. In this example, we have two locations with markers.
