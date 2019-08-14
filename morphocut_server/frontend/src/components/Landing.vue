<template>
  <div class="home">
    <vue-headful title="Home | MorphoCut"/>
    <img src="/static/morphocut_logo.png" style="width: 50%; margin-top: 5%; margin-bottom: 5%;">
    <div>MorphoCut is a platform to segment images of plankton and particles.</div>
    <b-button
      v-if="!this.$parent.user"
      size="lg"
      variant="primary"
      href="/login"
      style="margin-top: 5%;"
    >
      <font-awesome-icon icon="sign-in-alt"></font-awesome-icon>&nbsp;Login
    </b-button>
    <b-button v-else size="lg" variant="primary" to="/projects" style="margin-top: 5%;">Projects</b-button>
  </div>
</template>

<style>
.home {
  font-size: 2.5rem;
}
</style>


