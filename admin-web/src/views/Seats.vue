<!-- B3 座位管理（管理员D） -->
<template>
  <div class="card">
    <h3>座位管理</h3>
    <div style="margin-bottom:12px">
      筛选自习室：
      <select v-model="roomId" @change="load">
        <option :value="null">全部</option>
        <option v-for="r in rooms" :key="r.id" :value="r.id">{{ r.name }}</option>
      </select>
    </div>
    <div style="margin-bottom:16px; padding:10px; background:#fafafa; border:1px solid #eee; border-radius:4px">
      <strong>新增座位：</strong>
      目标自习室
      <select v-model="createRoomId">
        <option :value="null">请选择…</option>
        <option v-for="r in rooms" :key="r.id" :value="r.id">{{ r.name }}</option>
      </select>
      <input v-model="form.code" placeholder="座位编号" style="margin-left:8px" />
      <label style="margin-left:8px"><input type="checkbox" v-model="form.has_power" />带插座</label>
      <label style="margin-left:8px"><input type="checkbox" v-model="form.near_window" />靠窗</label>
      <button
        style="margin-left:8px"
        @click="create"
        :disabled="!createRoomId || !form.code"
        :title="!createRoomId ? '请选择目标自习室' : (!form.code ? '请填写座位编号' : '')"
      >新增</button>
      <span v-if="!createRoomId" style="color:#c00; margin-left:8px">← 请先选择目标自习室</span>
    </div>
    <table>
      <thead><tr><th>ID</th><th>教室</th><th>编号</th><th>插座</th><th>靠窗</th><th>状态</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="s in seats" :key="s.id">
          <td>{{ s.id }}</td>
          <td>{{ roomName(s.room_id) }}</td>
          <td>{{ s.code }}</td>
          <td>{{ s.has_power ? '✓' : '' }}</td>
          <td>{{ s.near_window ? '✓' : '' }}</td>
          <td>{{ s.is_active ? '可用' : '停用' }}</td>
          <td>
            <button class="secondary" v-if="s.is_active" @click="remove(s.id)">停用</button>
            <button v-else @click="reactivate(s.id)">启用</button>
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
const seats = ref([])
const roomId = ref(null)        // 列表筛选
const createRoomId = ref(null)  // 新增目标（与筛选解耦）
const form = ref({ code: '', has_power: false, near_window: false })

function roomName(id) { return rooms.value.find(r => r.id === id)?.name || id }

async function loadRooms() { rooms.value = (await http.get('/admin/rooms')).data }
async function load() {
  const q = roomId.value ? `?room_id=${roomId.value}` : ''
  seats.value = (await http.get(`/admin/seats${q}`)).data
}
async function create() {
  await http.post('/admin/seats', { ...form.value, room_id: createRoomId.value })
  form.value = { code: '', has_power: false, near_window: false }
  load()
}
async function remove(id) { await http.delete(`/admin/seats/${id}`); load() }
async function reactivate(id) { await http.post(`/admin/seats/${id}/reactivate`); load() }
onMounted(async () => { await loadRooms(); await load() })
</script>
