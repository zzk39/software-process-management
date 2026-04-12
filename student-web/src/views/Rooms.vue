<!-- A2 浏览自习室（学生A 负责） -->
<template>
  <div class="container">
    <div class="card">
      <h3>可用自习室</h3>
      <div v-if="rooms.length === 0">暂无可预约自习室</div>
      <div v-for="r in rooms" :key="r.id" class="room-item">
        <div>
          <div><strong>{{ r.name }}</strong>
            <span class="badge ok">{{ r.open_time }} - {{ r.close_time }}</span>
            <span class="badge warn" v-if="r.is_overnight">通宵</span>
            <span class="badge" v-if="r.department">{{ r.department }}</span>
          </div>
          <div style="color:#888; font-size:13px; margin-top:4px">{{ r.building }} · {{ r.floor }}</div>
        </div>
        <button @click="$router.push(`/rooms/${r.id}`)">查看座位</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../api'

const rooms = ref([])
onMounted(async () => { rooms.value = (await http.get('/rooms')).data })
</script>
