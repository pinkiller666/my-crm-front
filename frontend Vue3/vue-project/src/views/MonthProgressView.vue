<!-- src/views/MonthProgressView.vue -->
<template>
  <div class="month-progress-layout">
    <!-- Левая половина -->
    <div class="left-column">
      <ProgressSummary
          :orders="data_progress.total_orders"
          :amount="data_progress.total_amount"
          :goal="5000"
          :month="data_progress.month"
      />
    </div>

    <!-- Правая половина -->
    <div class="right-column">
      <AddProgressComm
        :artist-list="artist_list"
      />
      <p style="opacity: 0.3">Контейнер для формы</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import ProgressSummary from '@/components/ProgressSummary.vue'
import AddProgressComm from '@/components/AddProgressComm.vue'

const data_progress = ref({
  total_orders: 0,
  total_amount: 0,
  month: 0
})

/** @type {import('vue').Ref<Array<{ id: number, name: string }>>} */
const artist_list = ref([])

onMounted(async () => {
  try {
    const response_progress = await fetch('http://localhost:8000/api/progress/')
    const result_progress = await response_progress.json()
    data_progress.value = result_progress
  } catch (error) {
    console.error("Ошибка загрузки прогресса", error)
  }
  try {
    const response_artist = await fetch('http://localhost:8000/api/artists/')
    const result_artist = await response_artist.json()
    artist_list.value = result_artist
  } catch (error) {
    console.error("Ошибка загрузки списка художников", error)
  }
})
</script>


<style scoped>
.month-progress-layout {
  display: flex;
  width: 100%;
  height: 100%;
  padding: 2rem;
  gap: 2rem;
}

.left-column,
.right-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
  border: 4px dotted #f0f0f0;      /* очень светлый серый, почти белый */
  border-radius: 12px;
}
</style>


