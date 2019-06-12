import Vue from 'vue'
import App from './App.vue'
import router from './router'
import 'bootstrap/dist/css/bootstrap.css';
import BootstrapVue from 'bootstrap-vue';
import vueHeadful from "vue-headful";
import VueFormGenerator from "vue-form-generator"
import VuejsDialog from 'vuejs-dialog';
import {
  library
} from '@fortawesome/fontawesome-svg-core'
import {
  faUser,
  faPlus,
  faFolderPlus,
  faKey,
  faUsers,
  faSignOutAlt,
  faSignInAlt,
  faUpload,
  faImages,
  faDownload,
  faCogs,
  faFileDownload,
  faArrowDown,
  faStop,
  faTrash,
  faFileAlt
} from '@fortawesome/free-solid-svg-icons'
import {
  faGithub,
  faGithubSquare
} from '@fortawesome/free-brands-svg-icons'
import {
  FontAwesomeIcon
} from '@fortawesome/vue-fontawesome'

import 'vuejs-dialog/dist/vuejs-dialog.min.css';

library.add(faUser, faPlus, faFolderPlus, faKey, faUsers, faSignOutAlt, faUpload,
  faImages,
  faDownload,
  faCogs,
  faFileDownload,
  faArrowDown,
  faGithub,
  faStop,
  faSignInAlt,
  faGithubSquare,
  faTrash,
  faFileAlt
)

Vue.config.productionTip = false

Vue.use(BootstrapVue);
Vue.use(VuejsDialog);
Vue.use(VueFormGenerator, {
  validators: {
    range01: (value, field, model) => {
      if (value >= 0 && value <= 1) {
        return [];
      }
      return ['The input must be a number in the range from 0 to 1 (including 0 and 1)'];
    },
    positiveNumber: (value, field, model) => {
      if (value >= 0) {
        return [];
      }
      return ['The input must be a positive number'];
    }
  }
});

Vue.component('vue-headful', vueHeadful);
Vue.component('font-awesome-icon', FontAwesomeIcon)

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')