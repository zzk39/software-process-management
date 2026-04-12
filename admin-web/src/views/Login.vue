<template>
  <div class="login-box">
    <h2>管理端登录</h2>
    <input v-model="studentNo" placeholder="账号（默认 admin）" />
    <input v-model="password" type="password" placeholder="密码（默认 admin）" />
    <button @click="login">登 录</button>
    <p class="error" v-if="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '../api'

const studentNo = ref('admin')
const password = ref('admin')
const error = ref('')
const router = useRouter()

async function login() {
  try {
    const res = await http.post('/auth/login', { student_no: studentNo.value, password: password.value })
    if (!res.data.user.is_admin) throw new Error('非管理员账号')
    localStorage.setItem('admin_token', res.data.access_token)
    localStorage.setItem('admin_user', JSON.stringify(res.data.user))
    router.push('/rooms')
  } catch (e) {
    error.value = e.message
  }
}
</script>
