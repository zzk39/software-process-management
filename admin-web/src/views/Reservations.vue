<!-- B4 预约记录管理（zzk） -->
<template>
  <div class="card">
    <h3>预约记录</h3>
    <div style="margin-bottom:16px">
      <input v-model="q.student_no" placeholder="学号" />
      <input v-model="q.room_id" placeholder="自习室 ID" />
      <input v-model="q.date" placeholder="日期 YYYY-MM-DD" />
      <select v-model="q.status">
        <option value="">全部状态</option>
        <option value="PENDING">预约中</option>
        <option value="CHECKED_IN">已签到</option>
        <option value="CANCELLED">已取消</option>
        <option value="VIOLATED">违约</option>
      </select>
      <button @click="load">查询</button>
    </div>
    <table>
      <thead><tr><th>ID</th><th>用户</th><th>座位</th><th>教室</th><th>开始</th><th>结束</th><th>状态</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id">
          <td>{{ r.id }}</td>
          <td>{{ r.user_id }}</td>
          <td>{{ r.seat_id }}</td>
          <td>{{ r.room_id }}</td>
          <td>{{ fmt(r.start_at) }}</td>
          <td>{{ fmt(r.end_at) }}</td>
          <td>{{ r.status }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../api'

const rows = ref([])
const q = ref({ student_no: '', room_id: '', date: '', status: '' })

function fmt(s) { return s?.replace('T', ' ').slice(0, 16) }

async function load() {
  const params = Object.fromEntries(Object.entries(q.value).filter(([,v]) => v !== ''))
  rows.value = (await http.get('/admin/reservations', { params })).data
}
onMounted(load)
</script>
