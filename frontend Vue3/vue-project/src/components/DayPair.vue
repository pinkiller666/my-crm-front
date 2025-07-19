<template>
  <div class="day-pair" ref="pairRef" :class="typeClass" :data-date="date">
    <el-button circle class="my-other-button" :type="typeClass === 'day-off' ? 'success' : 'warning'">
      {{ weekday.toLowerCase() }}
    </el-button>

    <el-button circle ref="dayRef" type="info" class="my-other-button">
      {{ day }}
    </el-button>

    <!-- 📐 Выровненный контейнер -->
    <div class="task-container" ref="containerRef" :style="shiftStyles">
      <DayTaskList :tasks="props.tasks" ref="taskList" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, defineEmits, computed, defineExpose, nextTick } from 'vue'
import DayTaskList from './DayTaskList.vue'

const props = defineProps({
  weekday: String,
  date: String,
  day: Number,
  type: String,
  tasks: {
    type: Array,
    default: () => []
  }
})
const emit = defineEmits(['anchorReady'])

const taskList = ref<any>(null)
const pairRef = ref<HTMLElement | null>(null)
const containerRef = ref<HTMLElement | null>(null)
const dayRef = ref<any>(null)

const typeClass = computed(() => props.type ? `day-${props.type}` : '')

// reactive offsets
const shiftX = ref(0)
const shiftY = ref(0)

// update horizontal shift
function goRight() {
  let el: HTMLElement | undefined
  if (dayRef.value?.$el) {
    el = dayRef.value.$el as HTMLElement
  } else if (dayRef.value instanceof HTMLElement) {
    el = dayRef.value
  }
  if (el) {
    shiftX.value = el.offsetWidth / 2
  }
}

// update vertical shift
function goLower(offset: number) {
  shiftY.value += offset
  // adjust bottom padding to prevent overlap
  if (pairRef.value) {
    pairRef.value.style.paddingBottom = `${shiftY.value}px`
  }
  // recalc horizontal after potential layout change
  nextTick(() => goRight())
}

// compute combined transform style
const shiftStyles = computed(() => ({
  transform: `translateX(${shiftX.value}px) translateY(${shiftY.value}px)`
}))

// emit anchor ready
watch(pairRef, val => {
  if (val) emit('anchorReady', { date: props.date, el: val })
})
onMounted(() => {
  // initial horizontal shift
  nextTick(() => {
    goRight()
    if (pairRef.value) emit('anchorReady', { date: props.date, el: pairRef.value })
  })
})

defineExpose({
  taskList,
  goLower,
  goRight,
  containerRef,
  shiftY
})
</script>

<style scoped>
.day-pair {
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1rem;
  width: 40px;
  position: relative;
  pointer-events: none;
}

.my-other-button + .my-other-button {
  margin-left: 0 !important;
}

.my-other-button {
  font-size: smaller;
}

.day-week,
.day-number {
  width: 100%;
  text-align: center;
  padding: 4px 0;
  border-radius: 6px;
  font-size: 0.9rem;
  user-select: none;
  border: 2px solid #2c3e50;
}

.day-week {
  background: var(--bg-main);
  color: var(--text-secondary);
  font-weight: bold;
}

.day-number {
  background: var(--color-primary);
  color: white;
  font-weight: bold;
}

.day-pair.day-work .day-number {
  background: #ffdc4a;
  color: #2c3e50;
}

.day-pair.day-off .day-number {
  background: #8fd14f;
  color: #2c3e50;
}

.day-pair.day-holiday .day-number {
  background: #ffe79c;
  color: #8c6c00;
}

.day-pair.day-sick .day-number {
  background: #cce7f7;
  color: #23618c;
}

.task-container {
  position: relative;
  z-index: 20;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  transform: translateX(var(--shiftX)) translateY(var(--shiftY));
  will-change: transform;
  background: unset;
}
</style>
