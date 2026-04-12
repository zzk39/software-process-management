<!-- A5 取消 + A6 签到（林佳航） -->
<template>
  <div class="container">
    <div class="card">
      <h3>我的预约</h3>
      <table>
        <thead><tr><th>ID</th><th>座位</th><th>时间</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="r in list" :key="r.id">
            <td>{{ r.id }}</td>
            <td>#{{ r.seat_id }}（教室 {{ r.room_id }}）</td>
            <td>{{ fmt(r.start_at) }} ~ {{ fmt(r.end_at) }}</td>
            <td>
              <span class="badge" :class="statusCls(r.status)">{{ statusText(r.status) }}</span>
            </td>
            <td>
              <button v-if="r.status === 'PENDING'" class="secondary" @click="cancel(r.id)">取消</button>
              <button v-if="r.status === 'PENDING'" @click="openCheckin(r)" style="margin-left:6px">签到</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="card" v-if="checkinTarget">
      <h4>签到：预约 #{{ checkinTarget.id }}</h4>
      <p style="color:#666">请输入教室屏幕显示的动态码（开发环境可从管理端或数据库查看）</p>
      <input v-model="code" placeholder="动态签到码" style="width:200px" />
      <button @click="doCheckin" style="margin-left:8px">确认签到</button>
      <button class="secondary" @click="checkinTarget = null" style="margin-left:8px">关闭</button>
      <p class="error" v-if="err">{{ err }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../api'

const list = ref([])
const checkinTarget = ref(null)
const code = ref('')
const err = ref('')

const STATUS_MAP = {
  PENDING: ['待签到', ''], CHECKED_IN: ['已签到', 'ok'],
  CANCELLED: ['已取消', ''], VIOLATED: ['已违约', 'err'], FINISHED: ['已完成', 'ok']
}
function statusText(s) { return STATUS_MAP[s]?.[0] || s }
function statusCls(s) { return STATUS_MAP[s]?.[1] || '' }
function fmt(s) { return s.replace('T', ' ').slice(0, 16) }

async function load() { list.value = (await http.get('/reservations/me')).data }
async function cancel(id) { await http.post(`/reservations/${id}/cancel`); load() }

function openCheckin(r) { checkinTarget.value = r; code.value = ''; err.value = '' }
async function doCheckin() {
  err.value = ''
  try {
    await http.post('/checkin', { reservation_id: checkinTarget.value.id, code: code.value })
    checkinTarget.value = null
    load()
  } catch (e) { err.value = e.message }
}

onMounted(load)
</script>
