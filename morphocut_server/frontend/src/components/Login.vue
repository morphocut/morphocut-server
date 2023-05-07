<template>
  <div id="login-container" style="max-width: 400px; margin: 0 auto; padding: 20px;">
    <h2 style="font-size: 28px; margin-bottom: 20px;">Login</h2>
    <b-form @submit.prevent="onSubmit">
      <b-form-group id="email-group" label="Email:" label-for="email-input">
        <b-form-input
          id="email-input"
          type="email"
          v-model="loginForm.email"
          required
          placeholder="Enter email"
          style="font-size: 18px; width: 100%; max-width: 400px;"
        ></b-form-input>
      </b-form-group>

      <b-form-group id="password-group" label="Password:" label-for="password-input" style="margin-top: 20px;">
        <b-form-input
          id="password-input"
          type="password"
          v-model="loginForm.password"
          required
          placeholder="Enter password"
          style="font-size: 18px; width: 100%; max-width: 400px;"
        ></b-form-input>
      </b-form-group>

      <b-button type="submit" variant="primary" style="font-size: 20px; margin-top: 20px; width: 100%; max-width: 400px;">Login</b-button>
      <p v-if="errorMessage" style="color: red; margin-top: 20px;">{{ errorMessage }}</p>
    </b-form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      loginForm: {
        email: '',
        password: '',
      },
      errorMessage: '',
    };
  },
  methods: {
    async onSubmit() {
      try {
        const response = await axios.post('/api/login', {
          email: this.loginForm.email,
          password: this.loginForm.password,
        });

        if (response.data && response.data.access_token) {
          localStorage.setItem('access_token', response.data.access_token);
          this.$router.push('/users');
        } else {
          this.errorMessage = "Incorrect email or password.";
        }
      } catch (error) {
        console.error(error);
        this.errorMessage = "Unable to connect to server.";
      }
    },
  },
};
</script>
