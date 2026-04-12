<!-- A1 学生身份登录（学生A） -->
<template>
  <div class="login-box">
    <h2>学生端登录</h2>
    <input v-model="studentNo" placeholder="学号（默认 20230001）" />
    <input v-model="password" type="password" placeholder="密码（默认 123456）" />
    <button @click="login">登 录</button>
    <p class="error" v-if="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '../api'

const studentNo = ref('20230001')
const password = ref('123456')
const error = ref('')
const router = useRouter()

async function login() {
  try {
    const res = await http.post('/auth/login', { student_no: studentNo.value, password: password.value })
    localStorage.setItem('student_token', res.data.access_token)
    localStorage.setItem('student_user', JSON.stringify(res.data.user))
    router.push('/rooms')
  } catch (e) {
    error.value = e.message
  }
}
</script>
