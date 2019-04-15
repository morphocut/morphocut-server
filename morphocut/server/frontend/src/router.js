import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import Ping from '@/components/Ping';
import Upload from '@/components/Upload';
import Tasks from '@/components/Tasks';
import Project from '@/components/Project';
// import Datasets from '@/components/Datasets';
import Projects from '@/components/Projects';
import Accounts from '@/components/Accounts';

Vue.use(Router)

// @Christian: Read https://router.vuejs.org/guide/advanced/data-fetching.html#fetching-after-navigation

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [{
      path: '/',
      name: 'Projects',
      component: Projects
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
      path: '/tasks',
      name: 'Tasks',
      component: Tasks,
      props: {
        getAction: '/api/users/current/jobs',
        title: "Tasks",
        showProject: true
      },
    },
    {
      path: '/projects/:project_id/upload',
      name: 'Upload',
      component: Upload,
      props: (route) => ({
        project_id: parseInt(route.params.project_id)
      }),
    },
    {
      path: '/projects/:project_id',
      name: 'Project',
      component: Project,
      props: (route) => ({
        project_id: parseInt(route.params.project_id),
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