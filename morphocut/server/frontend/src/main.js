import Vue from 'vue'
import App from './App.vue'
import router from './router'
import 'bootstrap/dist/css/bootstrap.css';
import BootstrapVue from 'bootstrap-vue';
import vueHeadful from "vue-headful";

Vue.config.productionTip = false
Vue.use(BootstrapVue);
Vue.component('vue-headful', vueHeadful);

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')