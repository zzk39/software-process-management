import { createRouter, createWebHistory } from 'vue-router'
import Login from './views/Login.vue'
import Layout from './views/Layout.vue'
import Rooms from './views/Rooms.vue'
import RoomDetail from './views/RoomDetail.vue'
import MyReservations from './views/MyReservations.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    {
      path: '/',
      component: Layout,
      children: [
        { path: '', redirect: '/rooms' },
        { path: 'rooms', component: Rooms },              // A2 学生A
        { path: 'rooms/:id', component: RoomDetail },     // A4 林佳航
        { path: 'my', component: MyReservations }         // A5+A6 林佳航
      ]
    }
  ]
})

router.beforeEach((to) => {
  if (to.path !== '/login' && !localStorage.getItem('student_token')) {
    return '/login'
  }
})

export default router
