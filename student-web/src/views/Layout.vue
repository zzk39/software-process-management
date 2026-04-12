<template>
  <div>
    <nav class="navbar">
      <div>
        <router-link to="/rooms">自习室</router-link>
        <router-link to="/my">我的预约</router-link>
      </div>
      <div>
        <span style="margin-right:12px">{{ user.name }}（{{ user.department || '--' }}）</span>
        <a href="#" @click.prevent="logout">退出</a>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
const user = JSON.parse(localStorage.getItem('student_user') || '{}')
function logout() { localStorage.clear(); router.push('/login') }
</script>
