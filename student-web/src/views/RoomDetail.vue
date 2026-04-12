<!-- A4 创建预约（林佳航） -->
<template>
  <div class="container">
    <div class="card">
      <h3>{{ room?.name }}</h3>
      <div style="color:#888">{{ room?.building }} {{ room?.floor }} · {{ room?.open_time }}-{{ room?.close_time }}</div>
    </div>

    <div class="card">
      <h4>选择座位</h4>
      <div class="seat-grid">
        <div
          v-for="s in seats" :key="s.id"
          class="seat"
          :class="{ selected: selectedSeat?.id === s.id }"
          @click="selectedSeat = s"
        >
          <div><strong>{{ s.code }}</strong></div>
          <div style="font-size:12px; color:#666">
            <span v-if="s.near_window">🪟</span>
            <span v-if="s.has_power">🔌</span>
          </div>
        </div>
      </div>
    </div>

    <div class="card" v-if="selectedSeat">
      <h4>预约：{{ selectedSeat.code }}</h4>
      <div style="margin-bottom:10px">
        开始时间（整点）：
        <input type="datetime-local" v-model="startAt" step="3600" />
      </div>
      <div style="margin-bottom:10px">
        时长：
        <select v-model.number="hours">
          <option :value="1">1 小时</option>
          <option :value="2">2 小时</option>
          <option :value="3">3 小时</option>
          <option :value="4">4 小时</option>
        </select>
      </div>
      <button @click="submit">提交预约</button>
      <p class="error" v-if="error">{{ error }}</p>
      <p class="badge ok" v-if="success">预约成功！请按时签到。</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import http from '../api'

const route = useRoute()
const room = ref(null)
const seats = ref([])
const selectedSeat = ref(null)
const hours = ref(2)
const error = ref('')
const success = ref(false)

// 默认下一个整点
const now = new Date()
now.setHours(now.getHours() + 1, 0, 0, 0)
const pad = n => String(n).padStart(2, '0')
const startAt = ref(
  `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:00`
)

async function submit() {
  error.value = ''; success.value = false
  try {
    await http.post('/reservations', {
      seat_id: selectedSeat.value.id,
      start_at: new Date(startAt.value).toISOString(),
      hours: hours.value
    })
    success.value = true
  } catch (e) {
    error.value = e.message
  }
}

onMounted(async () => {
  room.value = (await http.get(`/rooms/${route.params.id}`)).data
  seats.value = (await http.get(`/rooms/${route.params.id}/seats`)).data
})
</script>
