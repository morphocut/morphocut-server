import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import Ping from '@/components/Ping';
import Upload from '@/components/Upload';
import Datasets from '@/components/Datasets';
import Projects from '@/components/Projects';
import Accounts from '@/components/Accounts';

Vue.use(Router)

// @Christian: Read https://router.vuejs.org/guide/advanced/data-fetching.html#fetching-after-navigation

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [{
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/tiles',
      name: 'tiles',
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import( /* webpackChunkName: "tiles" */ './views/Tiles.vue')
    },
    {
      path: '/ping',
      name: 'Ping',
      component: Ping,
    },
    {
      path: '/datasets',
      name: 'Datasets',
      component: Datasets,
    },
    {
      path: '/datasets/:dataset_id/upload',
      name: 'Upload',
      component: Upload,
      props: (route) => ({
        dataset_id: parseInt(route.params.dataset_id)
      }),
    },
    {
      path: '/projects',
      name: 'Projects',
      component: Projects,
    },
    {
      path: '/users',
      name: 'Accounts',
      component: Accounts,
    },
  ]
})