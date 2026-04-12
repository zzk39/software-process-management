<template>
  <div class="layout">
    <aside class="sidebar">
      <h2>自习座位管理</h2>
      <router-link to="/rooms">自习室管理</router-link>
      <router-link to="/seats">座位管理</router-link>
      <router-link to="/reservations">预约记录</router-link>
      <a href="#" @click.prevent="logout" style="margin-top:40px">退出登录</a>
    </aside>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
function logout() {
  localStorage.clear()
  router.push('/login')
}
</script>
