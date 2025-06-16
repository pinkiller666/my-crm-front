<template>
  <div class="day-pair" :class="typeClass" :data-date="date">
    <div class="day-week">{{ weekday }}</div>
    <div class="day-number">{{ day }}</div>

    <!-- 📌 Место для якоря -->
<!--    <div class="node-place" ref="nodeRef"></div>-->
    <!-- 📐 Выровненный контейнер -->
    <div class="task-container">
      <DayTaskList :tasks="props.tasks" ref="taskList"/>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, defineEmits, computed, defineExpose } from 'vue'
import DayTaskList from './DayTaskList.vue'

const taskList = ref<any>(null)  // компонент DayTaskList, НЕ HTMLElement

const props = defineProps({
  // День недели (например, "Пн")
  weekday: {
    type: String
  },
  // Дата в формате "2025-06-09"
  date: {
    type: String
  },
  // Номер дня месяца (например, 9)
  day: {
    type: Number
  },
  // Тип дня (например, "work", "off", "holiday", и т.д.)
  type: {
    type: String
    // default можно не задавать, если опционально
  },
  // Список задач для этого дня
  tasks: {
    type: Array,
    default: function() {
      // Если пропс не передан, используем пустой массив
      return [];
    }
  }
});

// 2. Потом всё остальное
const nodeRef = ref<HTMLElement | null>(null)
const emit = defineEmits(['anchorReady'])

// 3. watcher теперь безопасен (props точно есть)
watch(nodeRef, (val) => {
  if (val) emit('anchorReady', { date: props.date, el: val })
})

// 4. onMounted тоже ок
onMounted(() => {
  if (nodeRef.value) emit('anchorReady', { date: props.date, el: nodeRef.value })
})

// 👇 чтобы родитель мог достучаться
defineExpose({
  taskList,
  nodeRef
})

const typeClass = computed(() => {
  return props.type ? `day-${props.type}` : ''
})
</script>

<style scoped>
.day-pair {
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  width: 40px;
  position: relative;
  align-items: flex-start;
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
  color: #2c3e50;
  font-weight: bold;
}

.day-number {
  background: var(--color-primary);
  color: white;
  font-weight: bold;
}

/* 🎨 Раскраска по типу дня */
.day-pair.day-work .day-number {
  background: #ec8a4e;
  background: #ffdc4a;
  color: #fff1ec;
  color: #2c3e50;
}

.day-pair.day-off .day-number {
  background: #47a529;
  background: #8fd14f;
  color: #caf3c6;
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

/*.node-place {
  pointer-events: none;
  z-index: 1;
  height: 50px;
  width: 1px;
  background-color: blue;
  margin-top: -1rem;
}*/

.task-container {
  align-items: flex-start;
  z-index: 20;
  position: relative;
  left: 0%; /* по горизонтали — центр */
  //transform: translateX(50%);
  background-color: #ffe6e6;
  background: unset;
  margin-top: -1rem;

}
</style>
