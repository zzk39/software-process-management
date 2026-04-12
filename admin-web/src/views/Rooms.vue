<!-- B2 自习室管理（管理员D） -->
<template>
  <div class="card">
    <h3>自习室管理</h3>
    <div style="margin-bottom:16px">
      <input v-model="form.name" placeholder="名称" />
      <input v-model="form.building" placeholder="楼栋" />
      <input v-model="form.floor" placeholder="楼层" />
      <input v-model="form.department" placeholder="院系（空=全校）" />
      <input v-model="form.open_time" placeholder="开放 07:00" />
      <input v-model="form.close_time" placeholder="关闭 22:00" />
      <button @click="create">新增</button>
    </div>
    <table>
      <thead><tr><th>ID</th><th>名称</th><th>位置</th><th>时间</th><th>院系</th><th>状态</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="r in rooms" :key="r.id">
          <td>{{ r.id }}</td>
          <td>{{ r.name }}</td>
          <td>{{ r.building }} {{ r.floor }}</td>
          <td>{{ r.open_time }} - {{ r.close_time }}</td>
          <td>{{ r.department || '全校' }}</td>
          <td>{{ r.is_active ? '开放' : '停用' }}</td>
          <td>
            <button class="secondary" v-if="r.is_active" @click="remove(r.id)">停用</button>
            <button v-else @click="reactivate(r.id)">启用</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../api'

const rooms = ref([])
const form = ref({ name: '', building: '', floor: '', department: '', open_time: '07:00', close_time: '22:00' })

async function load() {
  const res = await http.get('/admin/rooms')
  rooms.value = res.data
}
async function create() {
  await http.post('/admin/rooms', form.value)
  form.value = { name: '', building: '', floor: '', department: '', open_time: '07:00', close_time: '22:00' }
  load()
}
async function remove(id) {
  await http.delete(`/admin/rooms/${id}`)
  load()
}
async function reactivate(id) {
  await http.post(`/admin/rooms/${id}/reactivate`)
  load()
}
onMounted(load)
</script>
