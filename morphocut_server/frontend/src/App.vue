<template>
  <div id="app">
    <b-navbar toggleable="md" type="dark" variant="dark" sticky>
      <b-navbar-toggle target="nav_collapse"></b-navbar-toggle>

      <b-navbar-brand to="/">
        <img
          src="/static/morphocut_logo.png"
          alt="MorphoCut"
          class="img-thumbnail"
          style="height: 2.5rem;"
        >
      </b-navbar-brand>

      <b-collapse is-nav id="nav_collapse">
        <b-navbar-nav>
          <b-nav-item v-if="user" to="/projects">Projects</b-nav-item>
          <!-- <b-nav-item v-if="user" to="/tasks">Tasks</b-nav-item> -->
          <!-- <b-nav-item to="/projects">Projects</b-nav-item> -->
        </b-navbar-nav>
        <b-navbar-nav v-if="user" class="ml-auto">
          <b-nav-item-dropdown right>
            <template slot="button-content">
              <font-awesome-icon icon="user"></font-awesome-icon>
              &nbsp;Logged in as {{user.email}}
            </template>

            <b-dropdown-item v-if="user.admin" to="/users">
              <font-awesome-icon icon="users"></font-awesome-icon>&nbsp;User Administration
            </b-dropdown-item>
            <b-dropdown-item href="/user/change-password">
              <font-awesome-icon icon="key"></font-awesome-icon>&nbsp;Change password
            </b-dropdown-item>
            <b-dropdown-item @click="logout">
              <font-awesome-icon icon="sign-out-alt"></font-awesome-icon>&nbsp;Logout
            </b-dropdown-item>
          </b-nav-item-dropdown>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>

    <router-view/>

    <b-navbar class="footer" toggleable="md" type="dark" variant="dark" fixed="bottom">
      <b-navbar-toggle target="nav_collapse"></b-navbar-toggle>

      <b-collapse is-nav id="nav_collapse">
        <b-navbar-nav style="margin: auto;">
          <b-nav-item to="/imprint">Imprint</b-nav-item>
          <b-nav-item href="https://github.com/morphocut/morphocut">
            <font-awesome-icon :icon="['fab', 'github']"></font-awesome-icon>&nbsp;Github
          </b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      user: {}
    };
  },
  methods: {
    logout() {
      const path = "/api/logout";
      console.log("Logging out, path: " + path);  // Add this line
      axios.get(path).then(() => {
        localStorage.removeItem('user_id');
        this.user = {};  // Clear the user data
        this.$router.push('/login');  // Redirect to the login page
      });
    },
    getCurrentUser() {
      const path = "/api/users/current";
      axios
        .get(path)
        .then(res => {
          this.user = res.data.user;
          console.log("current_user:");
          console.log(this.user);
        })
        .catch(error => {
          // eslint-disable-next-line
          console.error(error);
        });
    }
  },
  created() {
    this.getCurrentUser();
  }
};
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}

#header {
  position: -webkit-sticky;
  position: sticky;
  top: 0;
  z-index: 1071;
}
#sidebar {
  background: #fff;
  border-right: 1px solid #e5e5e5;
  border-bottom: 1px solid #e5e5e5;
}
@media (min-width: 768px) {
  #sidebar {
    position: -webkit-sticky;
    position: sticky;
    top: 3.5rem;
    z-index: 1000;
    max-height: calc(100vh - 3.5rem);
    border-right: 1px solid #e5e5e5;
    border-bottom: 1px solid #e5e5e5;
  }
}
#sidebar-nav {
  padding-top: 1rem;
  padding-bottom: 1rem;
  margin-right: -15px;
  margin-left: -15px;
  max-height: 100%;
  overflow-y: auto;
}
#sidebar-nav .nav {
  display: block;
}
#sidebar-nav .nav .nav-item .nav {
  display: none;
  margin-bottom: 1rem;
}
#sidebar-nav .nav .nav-item .nav {
  display: none;
  margin-bottom: 1rem;
}
#sidebar-nav .nav .nav-item.active .nav,
#sidebar-nav .nav .active + .nav {
  display: block;
}
@media (min-width: 768px) {
  #sidebar-nav .nav .nav-item .nav {
    display: block;
  }
}
#sidebar-nav .nav .nav-link.active,
#sidebar-nav .nav .active > .nav-link {
  color: #262626;
  font-weight: 500;
}
#sidebar-nav .nav-item .nav-link {
  padding: 0.25rem 1rem;
  font-weight: 500;
  color: #666;
}
#sidebar-nav .nav-item .nav-item .nav-link {
  font-weight: 400;
  font-size: 85%;
  margin-left: 1rem;
}
#main {
  padding-top: 1rem;
  margin-bottom: 2rem;
}
blockquote {
  margin-bottom: 1rem;
  font-size: 1.25rem;
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
}
pre {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 3px;
}
.modal-backdrop.fade {
  visibility: hidden;
}
.modal-backdrop.fade.show {
  visibility: visible;
}
.fade.show {
  display: block;
  /* z-index: 1; */
}
/* Add a black background color to the top navigation */
.topnav {
  background-color: #333;
  overflow: hidden;
}

/* Style the links inside the navigation bar */
.topnav a {
  float: left;
  color: #f2f2f2;
  text-align: center;
  padding: 14px 16px;
  text-decoration: none;
  font-size: 17px;
}

/* Change the color of links on hover */
.topnav a:hover {
  background-color: #ddd;
  color: black;
}

/* Add a color to the active/current link */
.topnav a.active {
  background-color: #4caf50;
  color: white;
}

.project .project-title {
  margin-bottom: 0.3rem;
  text-align: left;
}
.project .project-button {
  text-align: left;
  margin-top: auto;
  margin-bottom: auto;
}

.project .project-divider {
  height: 1px;
  background: darkgrey;
}

.project .project-image {
  max-width: 100%;
  max-height: 100%;
}

.project .card .card-title {
  font-size: 1rem;
  margin-bottom: 0.15rem;
}

.project .card .card-body {
  padding: 0.25rem;
}

.project .card {
  margin-bottom: 1rem;
}

.project {
  margin-left: 2rem;
  margin-right: 2rem;
}

.footer {
  font-size: 1rem;
  height: 2rem;
  text-align: center;
  color: darkgray;
}

.col-centered {
  margin: auto;
}

.row-no-margin {
  margin: 0 !important;
}

.dg-content-cont {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
}

.tab-pane {
  outline: none;
}
</style>
