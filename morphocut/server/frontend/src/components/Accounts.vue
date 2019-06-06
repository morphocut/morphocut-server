<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Users</h1>
        <hr>
        <br>
        <br>
        <button type="button" class="btn btn-success btn-sm" v-b-modal.user-modal>Add User</button>
        <br>
        <br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Email</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in users" :key="index">
              <td>{{ user.id }}</td>
              <td>{{ user.email }}</td>
              <td>
                <button
                  type="button"
                  class="btn btn-danger btn-sm"
                  style="margin-left: 0.5rem;"
                  v-on:click="removeUser(user.id)"
                >Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <b-modal ref="addUserModal" id="user-modal" title="Add a new user" hide-footer>
      <b-form @submit="onSubmit" @reset="onReset" class="w-100">
        <b-form-group id="form-email-group" label="Email:" label-for="form-email-input">
          <b-form-input
            id="form-email-input"
            type="text"
            v-model="addUserForm.email"
            required
            placeholder="Enter email"
          ></b-form-input>
        </b-form-group>
        <b-form-group id="form-password-group" label="Password:" label-for="form-password-input">
          <b-form-input
            id="form-password-input"
            type="password"
            v-model="addUserForm.password"
            required
            placeholder="Enter password"
          ></b-form-input>
        </b-form-group>
        <b-form-group id="form-admin-group" label="Admin? :" label-for="form-admin-input">
          <b-form-checkbox id="form-admin-input" v-model="addUserForm.admin"></b-form-checkbox>
        </b-form-group>
        <b-button type="submit" variant="primary">Submit</b-button>
        <b-button type="reset" variant="danger">Reset</b-button>
      </b-form>
    </b-modal>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      users: [],
      addUserForm: {
        email: "user@user.com",
        password: "password",
        admin: false
      }
    };
  },
  methods: {
    getUsers() {
      const path = "/api/users";
      axios
        .get(path)
        .then(res => {
          this.users = res.data.users;
          console.log(this.users);
        })
        .catch(error => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    addUser(payload) {
      const path = "/api/users";
      console.log(payload);

      axios
        .post(path, payload)
        .then(() => {
          this.getUsers();
        })
        .catch(error => {
          // eslint-disable-next-line
          console.log(error);
          this.getUsers();
        });
    },
    removeUser(user_id) {
      const path = "/api/users/" + user_id + "/remove";
      axios.get(path).then(res => {
        this.getUsers();
      });
    },
    initForm() {
      this.addUserForm.email = "";
      this.addUserForm.password = "";
      this.addUserForm.admin = false;
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addUserModal.hide();
      const payload = {
        email: this.addUserForm.email,
        password: this.addUserForm.password,
        admin: this.addUserForm.admin
      };
      console.log(payload);

      this.addUser(payload);
      this.initForm();
    },
    onReset(evt) {
      evt.preventDefault();
      this.$refs.addUserModal.hide();
      this.initForm();
    }
  },
  created() {
    this.getUsers();
  }
};
</script>