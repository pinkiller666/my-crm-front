<template>

<div class="calendar-wrapper">

  <div class="calendar-controls">
<el-date-picker
  v-model="selectedDate"
  type="month"
  placeholder="Выберите месяц"
  :disabled-date="disabledDate"
  size="small"
/>
    <el-select v-model="selectedUser" placeholder="Пользователь" size="small">
      <el-option
        v-for="user in userOptions"
        :key="user.id"
        :label="user.username || `ID ${user.id}`"
        :value="user.id"
      />
    </el-select>

    <el-segmented
      v-model="showDays"
      :options="[
        { label: 'Все', value: 'all' },
        { label: 'Будни', value: 'work' },
        { label: 'Выходные', value: 'off' }
      ]"
      size="small"
    />
    <el-segmented
      v-model="showScope"
      :options="[
        { label: 'Месяц', value: 'month' },
        { label: 'Неделя', value: 'week' }
      ]"
      size="small"
    />
    <el-checkbox v-model="doNotShowPast" label="С сегодня" size="small" />
  </div>

    <div class="counters" v-if="filteredDays.length">
      <span>Рабочие дни: {{ workDaysCount }}</span> |
      <span>Выходные: {{ offDaysCount }}</span> |
      <span>Рабочие часы: {{ totalWorkHours }}</span>
    </div>

  <div class="outer-container" v-if="filteredDays.length" v-loading="loading">
    <div class="month-header">
      <h2>📅 {{ monthOptions[selectedMonth - 1] }} {{ selectedYear }}</h2>
    </div>

<div class="month-scroll" >
    <div class="month-overview" v-drag-scroller ref="scrollContainer" @wheel="onWheel">
      <template v-for="(group, index) in groupedFilteredDays" :key="index">
        <div class="month-group">
          <DayPair
            v-for="day in group"
            :key="day.date"
            :day="day.day"
            :weekday="day.weekday"
            :type="day.type"
            :date="day.date"
            :tasks="tasks[day.date] || []"
            :class="{ 'forced-day': day.forced }"
                  @completeTask="handleCompleteTask"
      @removeTask="handleRemoveTask"
      @addTask="handleAddTask"
      @editTask="handleEditTask"
          />
        </div>
        <el-divider
          v-if="index !== groupedFilteredDays.length - 1"
          direction="vertical"
          class="group-divider"
        />
      </template>
    </div>

</div>
  </div>
</div>

<el-dialog
  v-model="isModalVisible"
  title="Редактировать задачу"
  width="600px"
  :close-on-click-modal="true"
  @close="closeModal"
  destroy-on-close
  close-on-press-escape
>
  <EventEditor
    v-if="currentTask"
    :initialEvent="currentTask"
    @complete="closeModal"
  />
</el-dialog>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import DayPair from './DayPair.vue'
import axios from "@/axios"
import EventEditor from './EventEditor.vue'
import { parseISO, getISOWeek } from 'date-fns'

// --- STATE ---
const selectedUser = ref(null)
const selectedDate = ref(null) // This will hold the selected month and year
const showDays = ref('all')        // all, work, off
const showScope = ref('month')     // month, week
const doNotShowPast = ref(false)
const userOptions = ref([])
const availableYears = ref([])
const availableMonths = ref([])
const days = ref([])
const groups = ref([])
const tasks = ref({})
const pattern = ref({})
const loading = ref(false)
const selectedYear = ref(null)
const selectedMonth = ref(null)
const scrollContainer = ref(null)
const isModalVisible = ref(false)
const currentTask = ref(null)
const showCancelled = ref(true)    // -<< ВАЖНОЕ

function isCancelledTask(item) {
  if (!item) {
    return false
  }

  // 1) overlay.status
  if (item.overlay && typeof item.overlay.status === 'string') {
    var s = item.overlay.status.toLowerCase()
    if (s === 'cancelled') {
      return true
    }
  }

  // 2) другие возможные поля/локации
  var candidates = [
    item.status,
    item.instance_status,
    item.state,
    item && item.event ? item.event.status : undefined
  ]

  for (var i = 0; i < candidates.length; i++) {
    var v = candidates[i]
    if (typeof v === 'string') {
      var vv = v.toLowerCase()
      if (vv === 'cancelled') {
        return true
      }
    }
  }

  // 3) флаг
  if (item.is_cancelled === true) {
    return true
  }

  return false
}


function handleEditTask(task) {
  console.log(task.event)
  currentTask.value = task.event
  isModalVisible.value = true
}

async function closeModal() {
  isModalVisible.value = false
  currentTask.value = null
    await loadAllEvents(selectedYear.value, selectedMonth.value)
}

const handleCompleteTask = async (task, newStatus) => {
  try {
    const payload = {
      status: newStatus ? 'complete' : 'incomplete',
      is_completed: newStatus,
      instance_datetime: task.datetime,
    }

    if (task.is_recurring) {
      await axios.patch(`/api/schedule/events/${task.event.id}/update-status/`, payload)
    } else {
      await axios.patch(`/api/schedule/events/${task.event.id}/`, {
        is_completed: newStatus,
        status: payload.status,
      })
    }

    await loadAllEvents(selectedYear.value, selectedMonth.value)
  } catch (err) {
    console.error('Не удалось обновить статус:', err)
  }
}


const handleRemoveTask = async (task) => {
  try {
    if (task.is_recurring) {
      // удаляем конкретное вхождение
      await axios.delete(`/api/schedule/events/${task.event.id}/delete/`, {
        params: { instance_datetime: task.datetime }
      })
    } else {
      // удаляем целое событие
      await axios.delete(`/api/schedule/events/${task.event.id}/delete/`)
    }

    await loadAllEvents(selectedYear.value, selectedMonth.value)
    console.log(`Task ${task.id} удалена!`)
  } catch (err) {
    console.error('Ошибка при удалении задачи:', err)
  }
}

const handleAddTask = async (task) => {
  try {
    await loadAllEvents(selectedYear.value, selectedMonth.value)
    console.log(`Task ${task.id} добавлено!`)
  } catch (err) {
    console.error('Ошибка при удалении задачи:', err)
  }
}

watch(selectedDate, (date) => {
  if (date instanceof Date) {
    selectedYear.value = date.getFullYear()
    selectedMonth.value = date.getMonth() + 1 // JS: 0-11, тебе надо 1-12
  }
})
watch([selectedYear, selectedMonth], ([year, month]) => {
  if (year && month) {
    selectedDate.value = new Date(year, month - 1)
  }
})
const disabledDate = (date) => {
  const y = date.getFullYear()
  const m = date.getMonth() + 1
  return !availableYears.value.includes(y) || !availableMonths.value.includes(m)
}
const monthOptions = [
  'Январь','Февраль','Март','Апрель','Май','Июнь',
  'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'
]

function onWheel(e) {
  const container = scrollContainer.value
  if (!container) return

  // прокручиваем горизонтально, если горизонталь больше вертикали
  if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
    container.scrollLeft += e.deltaY
  } else {
    container.scrollLeft += e.deltaX
  }
}

const filteredDays = computed(() => {
  const today = new Date()
  let list = days.value.slice()

  // filter out past
  if (doNotShowPast.value) {
    const todayLocal = new Date()
    const todayOnly = new Date(todayLocal.getFullYear(), todayLocal.getMonth(), todayLocal.getDate())
    list = list.filter(d => {
      const dd = parseISO(d.date) // d.date = 'YYYY-MM-DD'
      const ddOnly = new Date(dd.getFullYear(), dd.getMonth(), dd.getDate())
      return ddOnly >= todayOnly
    })
  }
  // filter by day type
  list = list.filter(d =>
    showDays.value === 'all' || d.type === showDays.value
  );
  // filter by scope
if (showScope.value === 'week') {
    const currentWeek = getISOWeek(new Date()); // Use new Date() for the current date
    list = list.filter(d => getISOWeek(parseISO(d.date)) === currentWeek);
}

  return list
})

const workDaysCount = computed(() => {
      return filteredDays.value.filter(day => day.type === 'work').length;
    })

const offDaysCount = computed(() => {
      return filteredDays.value.filter(day => day.type === 'off').length;
    })
const totalWorkHours = computed(() => {
      return workDaysCount.value * (pattern.value?.working_day_duration || 8);
    })

const groupedFilteredDays = computed(() => {
  // simple weekly grouping: split every 7 days
  const result = []
  const chunkSize = showScope.value === 'week' ? filteredDays.value.length : 7
  for (let i = 0; i < filteredDays.value.length; i += chunkSize) {
    result.push(filteredDays.value.slice(i, i + chunkSize))
  }
  return result
})

// --- LOAD AVAILABLE FILTERS ---
onMounted(async () => {
  try {
    const res = await axios.get('/api/schedule/month-schedules/');
    const data = res.data;

    const years = new Set(), months = new Set(), usersMap = new Map()
    for (const item of data) {
      years.add(item.year)
      months.add(item.month)
      if (item.user && !usersMap.has(item.user.id)) usersMap.set(item.user.id, item.user)
    }

    availableYears.value = [...years].sort()
    availableMonths.value = [...months].sort((a,b)=>a-b)
    userOptions.value = Array.from(usersMap.values())

    const today = new Date()
    const currentYear = today.getFullYear()
    const currentMonth = today.getMonth() + 1 // JS: 0–11 → 1–12

// если текущий год и месяц есть в доступных — используем их
    if (availableYears.value.includes(currentYear) && availableMonths.value.includes(currentMonth)) {
      selectedYear.value = currentYear
      selectedMonth.value = currentMonth
    } else {
      // иначе fallback — берём первые доступные
      selectedYear.value = availableYears.value[0]
      selectedMonth.value = availableMonths.value[0]
    }

    selectedUser.value = userOptions.value[0]?.id || null

  } catch (err) {
    ElMessage.error('Не удалось загрузить доступные данные 🥲')
    console.error(err)
  }
})


async function loadAllEvents(year, month) {
  loading.value = true
  try {
    const res = await axios.get(`/api/schedule/all_events/?year=${year}&month=${month}`)
    const data = res.data

    // ⛔️ 1) фильтруем отменённые (cancelled)
    const visible = []
    for (let i = 0; i < data.length; i++) {
      const item = data[i]
      if (item && (showCancelled.value || !isCancelledTask(item))) {
        visible.push(item)
      }
    }

    // 📅 2) собираем по датам только видимые
    const tasksByDate = {}
    for (let i = 0; i < visible.length; i++) {
      const dt = new Date(visible[i].datetime)
      const dateKey = toLocalDateKey(dt)
      if (!tasksByDate[dateKey]) {
        tasksByDate[dateKey] = []
      }
      tasksByDate[dateKey].push(visible[i])
    }

    tasks.value = tasksByDate
  } catch (err) {
    ElMessage.error('Не удалось загрузить таски из all_events 🥲')
    console.error(err)
  } finally {
    loading.value = false
  }
}


// --- WATCH FILTERS & LOAD DAYS ---
watch([selectedUser, selectedMonth, selectedYear], async ([user, month, year]) => {
  if (!user || !month || !year) return
  loading.value = true
  try {
    const res = await axios.get(
      `/api/schedule/preview?year=${year}&month=${month}&user=${user}`
    )
    const data = res.data;
    days.value = data.days
    groups.value = data.groups
    pattern.value = data.pattern
    tasks.value = data.tasks || {}

    // 🛡️ выкидываем cancelled из предварительных tasks (если они пришли из /preview)
    if (tasks.value && typeof tasks.value === 'object') {
      const cleaned = {}
      const keys = Object.keys(tasks.value)
      for (let i = 0; i < keys.length; i++) {
        const k = keys[i]
        const arr = tasks.value[k]
        if (Array.isArray(arr)) {
          const kept = []
          for (let j = 0; j < arr.length; j++) {
            const t = arr[j]
            if (t && (showCancelled.value || t.status !== 'cancelled')) {
              kept.push(t)
            }
          }
          if (kept.length > 0) {
            cleaned[k] = kept
          }
        }
      }
      tasks.value = cleaned
    }

    await loadAllEvents(year, month)

    await nextTick()
  } catch (err) {
    ElMessage.error('Не удалось загрузить расписание 😢')
    console.error(err)
  } finally {
    loading.value = false
  }
}, { immediate: true })

function toLocalDateKey(dateObj) {
  const y = dateObj.getFullYear()
  const m = String(dateObj.getMonth() + 1).padStart(2, '0')
  const d = String(dateObj.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}` // YYYY-MM-DD в локальной зоне
}

</script>

<style scoped>
.outer-container {
  width: 100%;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  box-sizing: border-box;
}

.month-header {
  margin-bottom: 2rem;
  text-align: center;
}

.month-scroll {
  position: relative;
  scroll-behavior: smooth;
  max-width: 90vw;
  mask-image: linear-gradient(to right, transparent, black 7%, black 93%, transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, black 7%, black 93%, transparent);
  overflow-x: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE 10+ */
}


.month-overview {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  gap: 1.5rem;
  padding: 1rem 0;
  overflow-x: auto;
  overflow-y: hidden;
  flex-wrap: nowrap;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE 10+ */
  padding: 0 30vw;
}

.month-overview::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.month-group {
  position: relative;
  display: flex;
  flex-direction: row;
  gap: 0.4rem;
  align-items: flex-start;
  transition: transform 0.3s ease;
}

.group-divider {
  height: auto;
  align-self: stretch;
  margin: 0 -0.6rem;
}

.calendar-controls {
  display: flex;
  flex-wrap: nowrap;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.calendar-controls .el-select {
  min-width: 120px;
  max-width: 150px;
  height: 32px;
  font-size: 14px;
}

.day-number {
  position: relative;
}
</style>


<style>
.content-wrapper{
    display: flex;
  align-items: center;
  justify-content: center;
}
</style>
