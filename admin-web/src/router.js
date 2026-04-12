import { createRouter, createWebHistory } from 'vue-router'
import Login from './views/Login.vue'
import Layout from './views/Layout.vue'
import Rooms from './views/Rooms.vue'
import Seats from './views/Seats.vue'
import Reservations from './views/Reservations.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    {
      path: '/',
      component: Layout,
      children: [
        { path: '', redirect: '/rooms' },
        { path: 'rooms', component: Rooms },       // B2 管理员D
        { path: 'seats', component: Seats },       // B3 管理员D
        { path: 'reservations', component: Reservations } // B4 zzk
      ]
    }
  ]
})

router.beforeEach((to) => {
  if (to.path !== '/login' && !localStorage.getItem('admin_token')) {
    return '/login'
  }
})

export default router
