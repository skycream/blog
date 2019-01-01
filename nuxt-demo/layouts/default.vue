<template>
  <nuxt class="container" />
</template>

<style lang="scss">
// Cool
$aqua: #81d4fa;
$blue: #2196f3;
$navy: #1a237e;
$teal: #009688;
$green: #4caf50;
$olive: #33691e;
$lime: #cddc39;

// Warm
$yellow: #ffeb3b;
$orange: #ff9800;
$red: #f44336;
$fuchsia: #c51162;
$purple: #9c27b0;
$maroon: #b71c1c;

// Gray Scale
$white: #ffffff;
$silver: #eeeeee;
$gray: #9e9e9e;
$black: #424242;

// Colors (from /themes/default/colors)
$picnic-white: #ffffff;
$picnic-black: #424242;
$picnic-primary: $blue;
$picnic-success: $green;
$picnic-warning: $orange;
$picnic-error: $red;
$picnic-dull: $gray;
$picnic-color-variation: 10%;
$picnic-transparency: 0.25;

// Spaces
$picnic-separation: 0.5rem;
$picnic-breakpoint: 50em;

// Shapes
$picnic-radius: 0.25rem;
$picnic-border: 1px solid #e0e0e0;
$picnic-shadow: 0 0 0.25rem rgba($picnic-black, $picnic-transparency);

// Transitions
$picnic-transition: all 0.3s;

// Imports the base variable styles
@import "../node_modules/picnic/src/themes/default/theme";

@import "../node_modules/picnic/src/vendor/compass-breakpoint/stylesheets/breakpoint";

// Normalize.css (external library)
@import "../node_modules/picnic/src/plugins/normalize/plugin";

// Generic styles for things like <body>, <a> and others
// It also overwrites normalize.css a bit
@import "../node_modules/picnic/src/plugins/generic/plugin";
@import "../node_modules/picnic/src/plugins/fontello/plugin";

// Simple elements
@import "../node_modules/picnic/src/plugins/label/plugin";
@import "../node_modules/picnic/src/plugins/button/plugin";

// Forms
// @import "../node_modules/picnic/src/plugins/input/plugin";
// @import "../node_modules/picnic/src/plugins/select/plugin";
@import "../node_modules/picnic/src/plugins/radio/plugin";
// @import "../node_modules/picnic/src/plugins/checkbox/plugin";

// Components
@import "../node_modules/picnic/src/plugins/table/plugin";
@import "../node_modules/picnic/src/plugins/grid/plugin";

// Extra
// @import "../node_modules/picnic/src/plugins/nav/plugin";

// @import "../node_modules/picnic/src/plugins/stack/plugin";
@import "../node_modules/picnic/src/plugins/card/plugin";
// @import "../node_modules/picnic/src/plugins/modal/plugin";

// @import "../node_modules/picnic/src/plugins/dropimage/plugin";
@import "../node_modules/picnic/src/plugins/tabs/plugin";
// @import "../node_modules/picnic/src/plugins/tooltip/plugin";

html,
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
    Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;
  -webkit-font-smoothing: antialiased;
}

.container {
  margin: 0 auto;
  max-width: 992px;
  padding: 2rem 2.5rem;
}
</style>
