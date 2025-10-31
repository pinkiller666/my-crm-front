<template>
  <div class="day" ref="containerRef">
    <div
      class="calendar-day"
      :class="[typeClass, { 'today': isToday }]"
      @click="showForm = true; focusNextTick()"
    >
      <div class="day-number">{{ day }}</div>
      <div class="day-weekday">{{ weekday.toLowerCase() }}</div>
    </div>

    <DayTaskList
      v-if="tasks.length"
      :tasks="tasks"
      :date="date"
      @completeTask="handleCompleteTask"
      @removeTask="handleRemoveTask"
      @addTask="handleAddTask"
      @editTask="handleEditTask"
    />

    <!-- Overlay -->
    <Teleport to="body">
    <div v-if="showForm" class="overlay" @click.self="cancelAdd">
      <div class="task-form" @keydown.enter="submitTask" @click.stop>
        <h3>Событие на {{ formattedDate }}</h3>


        <el-input
          v-model="form.name"
          placeholder="Название"
          ref="titleInputRef"
        />

        <el-input
          v-model="form.description"
          placeholder="Описание"
        />

        <el-time-picker
          v-model="form.time"
          placeholder="Выбери время"
          format="HH:mm"
          value-format="HH:mm"
          ref="timeInputRef"
        />

        <el-button type="primary" @click="submitTask">Сохранить</el-button>
      </div>
    </div>
  </Teleport>
  </div>
</template>


<script setup lang="ts">
import { ref, onMounted, watch, computed, nextTick, onBeforeUnmount } from 'vue'
import DayTaskList from './DayTaskList.vue'
import axios from '@/axios'

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

const emit = defineEmits(['deleteTask', 'completeTask', 'addTask', 'editTask'])

const taskList = ref<any>(null)
const containerRef = ref<HTMLElement | null>(null)
const dayRef = ref<any>(null)

const typeClass = computed(() => props.type ? `day-${props.type}` : '')

const isToday = computed(() => {
      const today = new Date()
      const dayDate = new Date(props.date)
      return (
        today.getFullYear() === dayDate.getFullYear() &&
        today.getMonth() === dayDate.getMonth() &&
        today.getDate() === dayDate.getDate()
      )
    })

const timeInputRef = ref(null)
const titleInputRef = ref(null)
const addButtonRef = ref(null)
const showForm = ref(false)
const form = ref({
  time: '',
  name: '',
  description: ''
})

const formattedDate = computed(() => {
  const d = new Date(props.date)
  return d.toLocaleDateString('ru-RU', {
    weekday: 'long',
    day: 'numeric',
    month: 'long'
  })
})

function focusNextTick() {
  nextTick(() => {
    titleInputRef.value?.focus?.()
  })
}

function cancelAdd() {
  showForm.value = false
  form.value = { time: '', name: '', description: '' }
}
async function submitTask() {
  if (!form.value.time || !form.value.name) return

  try {
    const [hh, mm] = form.value.time.split(':')
    const dateObj = new Date(props.date)
    dateObj.setHours(Number(hh), Number(mm), 0, 0)

    const isoDatetime = dateObj.toISOString()

    const payload = {
      name: form.value.name,
      description: form.value.description,
      start_datetime: isoDatetime
    }

    const response = await axios.post('schedule/events/', payload)

    emit('addTask', response.data)

    // Очищаем форму, но оставляем открытой
    form.value = { time: '', name: '', description: '' }
    focusNextTick()
  } catch (err) {
    console.error('Ошибка при добавлении задачи:', err)
  }
}



// Event handlers to pass events up to the parent
const handleCompleteTask = (task, isChecked) => {
  emit('completeTask', task, isChecked)
}

const handleRemoveTask = (taskId) => {
  emit('removeTask', taskId)
}

const handleAddTask = (newTask) => {
  emit('addTask', newTask)
}

const handleEditTask = (updatedTask) => {
  emit('editTask', updatedTask)
}

// закрытие по Escape
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    cancelAdd()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})

</script>

<style lang="scss" scoped>
.calendar-day {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  /* чутка больше «кликабельной» площади */
  width: 44px;
  height: 56px;

  padding: 4px;
  border-radius: 10px;
  font-family: inherit;
  user-select: none;
  transition: background 0.2s ease, transform 0.1s ease;
  cursor: pointer;

  /* базовые цвета (можно позже заменить на CSS-переменные темы) */
  --num-bg: transparent;
  --num-fg: #23262f;

  &:hover { background: #f5f7fa; }
  &.today { border: 2px solid #409eff; border-radius: 10px; }

  /* типы дней – меняем только цвет цифры, фон оставляем нейтральным */
  &.day-off      { --num-fg: #32d60d; }
  &.day-holiday  { --num-fg: #8c6c00; }
  &.day-sick     { --num-fg: #23618c; }

  /* САМА ЦИФРА */
  .day-number {
    font-size: 18px;
    font-weight: 700;
    line-height: 1;
    color: var(--num-fg);
    background: var(--num-bg);
    padding: 4px 8px;
    border-radius: 999px;   /* мягкий «пилюля»-бейдж */
    display: inline-block;
    transform: translateZ(0);
  }

  /* СЕГОДНЯ — инвертируем цвета бейджа, чтобы бросалось в глаза */
  &.today .day-number {
    --num-bg: #409eff;
    --num-fg: #fff;
  }

  .day-weekday {
    font-size: 12px;
    color: #8c8c8c;
    text-transform: lowercase;
    margin-top: 3px;
  }

  /* маленький «прыг» при нажатии (ощущение отклика) */
  &:active { transform: translateY(1px); }
}


.overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.task-form {
  background: #fff;
  padding: 24px;
  border-radius: 12px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-form h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.calendar-day.today {
  border: 2px solid #409eff;
  border-radius: 6px;
}

.calendar-day.today .day-number {
  position: relative;
  display: inline-block;
}

/* бейдж "сегодня" добавлен ПСЕВДОЭЛЕМЕНТОМ (только CSS) */
.calendar-day.today .day-number::before {
  content: "сегодня";  /* поменяешь на "today", если захочешь */
  position: absolute;
  top: -14px;
  left: 0;
  padding: 2px 8px;
  font-size: 11px;
  line-height: 1;
  border-radius: 9999px;
  background: rgba(0, 150, 255, 0.12);
  border: 1px solid rgba(0, 150, 255, 0.35);
  color: #0b6fbf;
  font-weight: 600;
  pointer-events: none;
  text-transform: lowercase;
}
</style>
