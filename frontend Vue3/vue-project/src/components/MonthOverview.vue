<template>
  <div class="calendar-controls">
    <el-select v-model="selectedYear" placeholder="Год" size="small">
      <el-option v-for="y in [2025, 2026]" :key="y" :label="y" :value="y" />
    </el-select>
    <el-select v-model="selectedMonth" placeholder="Месяц" size="small">
      <el-option
          v-for="(label, index) in monthOptions"
          :key="index"
          :label="label"
          :value="index + 1"
      />
    </el-select>
    <el-select v-model="selectedUser" placeholder="Пользователь" size="small">
      <el-option
          v-for="user in userOptions"
          :key="user.id"
          :label="user.name"
          :value="user.id"
      />
    </el-select>
    <el-select v-model="displayMode" placeholder="Режим" size="small">
      <el-option label="Все дни" value="all" />
      <el-option label="Только будни" value="work" />
      <el-option label="Только выходные" value="off" />
    </el-select>
  </div>

  <div class="outer-container">
    <div class="month-header">
      <h2>📅 {{ monthOptions[selectedMonth - 1] }} {{ selectedYear }}</h2>
    </div>

    <div class="month-overview">
      <template v-for="(group, index) in groupedDays" :key="index">
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
          />
        </div>
        <el-divider
            v-if="index !== groupedDays.length - 1"
            direction="vertical"
            class="group-divider"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick, onUnmounted } from 'vue'
import DayPair from './DayPair.vue'

const selectedUser = ref<number | null>(null)
const selectedMonth = ref(6)
const selectedYear = ref(2025)
const displayMode = ref('all')
const userOptions = ref<{ id: number; name: string }[]>([])

const monthGroupRefs: HTMLElement[] = []

const monthOptions = [
  'Январь', 'Февраль', 'Март', 'Апрель',
  'Май', 'Июнь', 'Июль', 'Август',
  'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
]

const tasks = ref<Record<string, string[]>>({
  "2025-06-04": ["Зарегистрировать себя как вселенную", "Перевести муху на другой язык", "Зарегистрировать себя как вселенную"],
  "2025-06-06": ["Открыть портал в параллельную вселенную, где понедельники отменены", "Зарегистрировать себя как вселенную", "Убежать от забот"],
  "2025-06-08": ["Поспать стоя", "Убежать от забот", "Устроить войну пузырей"],
  "2025-06-09": ["Устроить войну пузырей", "Заколдовать кота", "Убежать от забот"],
  "2025-06-12": ["Зарегистрировать себя как вселенную"],
  "2025-06-13": ["Создать гильдию ленивцев", "Погладить шнурки", "Отрастить двухметровые крылья, хвост, уши и научиться мурлыкать", "Создать гильдию ленивцев", "Найти смысл в банане", "Убедить облако что ты — не еда", "Съесть чай"],
  "2025-06-17": ["Съесть чай"],
  "2025-06-19": ["Стать драконом", "Составить стратегию по захвату дивана и обороне от понедельников", "Создать гильдию ленивцев", "Съесть чай"],
  "2025-06-21": ["Заварить кефир", "Убедить облако что ты — не еда", "Устроить войну пузырей", "Перевести муху на другой язык", "Зарегистрировать себя как вселенную", "Создать гильдию ленивцев"],
  "2025-06-22": ["Стать драконом", "Найти смысл в банане"],
  "2025-06-23": ["Стать драконом", "Поймать тень", "Поспать стоя"],
  "2025-06-25": ["Убежать от забот", "Съесть чай"],
  "2025-06-27": ["Найти смысл в банане"],
  "2025-06-28": ["Разморозить мороженное", "Не купить Скайрим", "Отрастить двухметровые крылья, хвост, уши и научиться мурлыкать"],
  "2025-06-29": ["Открыть портал в параллельную вселенную, где понедельники отменены", "Поспать стоя"]
})

interface ApiDay {
  date: string
  day: number
  weekday: string
  type: string
  forced?: boolean
}

const days = ref<ApiDay[]>([])
const groups = ref<number[]>([])


const groupedDays = computed(() => {
  const result: ApiDay[][] = []
  let startIndex = 0
  if (!Array.isArray(groups.value)) return result
  for (const size of groups.value) {
    result.push(days.value.slice(startIndex, startIndex + size))
    startIndex += size
  }
  return result
})

watch([
  selectedUser,
  selectedMonth,
  selectedYear
], async ([user, month, year]) => {
  if (!user || !month || !year) return
  try {
    const res = await fetch(`/api/schedule/preview?year=${year}&month=${month}&user=${user}`)
    const data = await res.json()
    days.value = data.days
    groups.value = data.groups
    await nextTick()
  } catch (err) {
    console.error('Ошибка при загрузке расписания:', err)
  }
}, { immediate: true })

onMounted(async () => {
  const scheduleRes = await fetch(`/api/schedule/preview?year=2025&month=5`)
  const scheduleData = await scheduleRes.json()
  days.value = scheduleData.days
  groups.value = scheduleData.groups

  const usersRes = await fetch('/api/users-with-schedule/')
  const usersData = await usersRes.json()
  userOptions.value = usersData.map((u: any) => ({ id: u.id, name: u.name }))

})
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

.month-overview {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  gap: 1.5rem;
  padding: 1rem 0;
  overflow-x: auto;
  flex-wrap: nowrap;
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
