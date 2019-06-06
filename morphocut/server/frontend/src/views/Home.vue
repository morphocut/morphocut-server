<template>
  <div class="home">
    <!-- <HelloWorld msg="Welcome to Your Vue.js App"/> -->
    <!-- <button type="button" class="btn btn-primary">Button</button> -->
    <div>
      <img alt="Vue logo" src="../assets/logo.png">
    </div>
    <div>
      <h1>morphocut</h1>
    </div>
    <div class="col col-12">
      <div class="row">
        <div class="centering">
          <b-button to="/datasets" variant="primary">Datasets</b-button>
          <b-button to="/projects" variant="primary">Projects</b-button>
        </div>
      </div>
      <div class="row">
        <div class="divider"></div>
      </div>
      <div class="row">
        <div class="centering">
          <b-button to="/tiles">Tiles</b-button>
          <b-button :to="{ name: 'Ping', params: { userId: 123 }}">Ping</b-button>
          <b-button to="/upload">Upload</b-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// @ is an alias to /src

export default {
  name: "home"
};
</script>

<style>
.btn {
  margin: 2px;
}
.row {
  margin: 0.5rem;
}
.centering {
  text-align: center;
  width: 100%;
}
.divider {
  position: absolute;
  height: 1px;
  width: 80%;
  left: 10%;
  background: grey;
}
</style>

