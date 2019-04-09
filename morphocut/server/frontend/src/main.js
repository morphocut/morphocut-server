import Vue from 'vue'
import App from './App.vue'
import router from './router'
import 'bootstrap/dist/css/bootstrap.css';
import BootstrapVue from 'bootstrap-vue';
import VueMultiselect from "vue-multiselect";

Vue.config.productionTip = false
Vue.use(BootstrapVue);
Vue.component("multiSelect", VueMultiselect.default);

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')