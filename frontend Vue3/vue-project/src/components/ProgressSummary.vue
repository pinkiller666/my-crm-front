<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

function formatWithSpacesAndDollar(x: number): string {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + '$'
}

const props = withDefaults(defineProps<{
  orders: number
  amount: number
  goal?: number
  month?: number
  unit?: string
}>(), {
  goal: 5000,
  month: new Date().getMonth() + 1,
  unit: '$'
})

const progress = computed(() => {
  if (!props.amount || !props.goal) return 0
  return Math.round(Math.min((props.amount / props.goal) * 100, 100))
})

const status = computed(() => {
  return progress.value >= 100 ? 'success' : ''
})

function getColor() {
  const result = getComputedStyle(document.documentElement).getPropertyValue('--color-success').trim()
  console.log('[color-success]', result)
  return result
}

const progressColor = ref(getColor())

const observer = new MutationObserver(() => {
  progressColor.value = getColor()
})

onMounted(() => {
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
})



onBeforeUnmount(() => observer.disconnect())
</script>

<template>
  <div class="progress-summary themed-box">
    <div class="progress-header">
      <span class="label">Прогресс по сумме</span>
      <span class="value">
        {{ formatWithSpacesAndDollar(props.amount) }} из {{ formatWithSpacesAndDollar(props.goal) }}
      </span>
    </div>

    <el-progress
        :key="progressColor"
        :percentage="progress"
        :stroke-width="24"
        :text-inside="true"
        :status="status"
        :stroke-color="progressColor"
        type="line"
    />
  </div>
</template>


<style scoped>
.progress-summary {
  width: 100%;
  padding: 1.5rem;
  max-width: 700px;
  box-sizing: border-box;
  border-radius: var(--radius-card, 8px);
  background: var(--bg-secondary);
  color: var(--text-main);
}

:deep(.el-progress-bar__inner) {
  background-color: var(--el-color-primary) !important;
}

/* Всё, что внутри — themed */
.progress-summary * {
  user-select: none;
  color: var(--text-main);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.label {
  opacity: 0.8;
}

.value {
  font-weight: bold;
}
</style>
