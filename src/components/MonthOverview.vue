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
      <el-select
          v-if="showUserSelector"
          v-model="selectedUser"
          placeholder="Пользователь"
          size="small"
          :disabled="userSelectorLocked"
      >
        <el-option
            v-for="user in userOptions"
            :key="user.id"
            :label="user.name || user.username || ('ID ' + user.id)"
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
      <el-checkbox
          v-model="doNotShowPast"
          label="С сегодня"
          size="small"
      />
    </div>



    <div class="outer-container" v-if="filteredDays.length" v-loading="loading">


        <div class="month-header">
          <h2>📅 {{ monthOptions[selectedMonth - 1] }} {{ selectedYear }}</h2>
          <div
              class="month-summary-clickzone"
              role="button"
              tabindex="0"
              @click="openScheduleDialog"
              @keydown.enter="openScheduleDialog"
              @keydown.space.prevent="openScheduleDialog"
          >
          <StatsChips
              v-if="summary"
              :summary="summary"
          />
        </div>
      </div>
      <!-- 👇 новый общий контейнер под таймлайном и месячными событиями -->
      <div class="month-body">
        <div class="month-scroll">
          <div
              class="month-overview"
              v-drag-scroller
              ref="scrollContainer"
              @wheel="onWheel"
          >
            <template
                v-for="(group, index) in groupedFilteredDays"
                :key="index"
            >
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

        <!-- 👇 MonthlyEvents: под таймлайном, выровнен по его левому краю, вне скролла -->
        <MonthlyEvents
            v-if="monthlyEvents.length"
            :events="monthlyEvents"
            @edit="handleEditMonthly"
            @remove="handleRemoveMonthly"
        />
      </div>
    </div>

    <el-dialog
        v-model="isScheduleDialogOpen"
        title="Текущее расписание"
        width="520px"
        :close-on-click-modal="true"
        destroy-on-close
        close-on-press-escape
    >
      <div class="schedule-dialog-body">
        <div class="schedule-subtitle">
          {{ monthOptions[selectedMonth - 1] }} {{ selectedYear }}
        </div>

        <div class="schedule-row">
          <div class="schedule-value">{{ patternText }}</div>
        </div>

        <div class="schedule-actions">
          <el-button type="primary" @click="openTemplatePicker">
            Сменить шаблон
          </el-button>
        </div>
      </div>
    </el-dialog>



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
  </div>
</template>


<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import DayPair from './DayPair.vue'
import axios from '@/axios'
import EventEditor from './EventEditor.vue'
import { parseISO, getISOWeek } from 'date-fns'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import StatsChips from './StatsChips.vue'
import MonthlyEvents from './MonthlyEvents.vue'

import { useDevFlags } from '@/composables/useDevFlags'

const { devFlags } = useDevFlags()

// --- STATE ---
const authStore = useAuthStore()
const { user: currentUser } = storeToRefs(authStore)

const today = new Date()
const summary = ref(null)

const selectedUser = ref(null)
const selectedDate = ref(new Date(today.getFullYear(), today.getMonth()))
const showDays = ref('all')        // all | work | off
const showScope = ref('month')     // month | week
const doNotShowPast = ref(false)

const userOptions = ref([])
const userSelectorLocked = ref(true)
const availableYears = ref([])
const availableMonths = ref([])

const days = ref([])
const groups = ref([])
const tasks = ref({})
const pattern = ref({})
const loading = ref(false)

const selectedYear = ref(today.getFullYear())
const selectedMonth = ref(today.getMonth() + 1)

const scrollContainer = ref(null)
const isModalVisible = ref(false)
const currentTask = ref(null)
const showCancelled = ref(true) // показывать ли отменённые

const monthOptions = [
  'Январь','Февраль','Март','Апрель','Май','Июнь',
  'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'
]

// ====== 🔧 Временный оверрайд расписания (включить/выключить) ======
const USE_TEMP_OVERRIDE = false

// --- MONTHLY SPLIT ---
function isMonthlyEvent(obj) {
  if (!obj) return false

  // верхнего уровня метка
  if (typeof obj.recurrence_type === 'string' &&
      obj.recurrence_type.toLowerCase() === 'monthly') {
    return true
  }

  // вложенный event
  const ev = (obj && obj.event) ? obj.event : null
  if (ev) {
    if (ev.is_recurring_monthly === true) return true

    // частный протокол твоего проекта
    if (typeof ev.date_mode === 'string') {
      const dm = ev.date_mode.toLowerCase()
      if (dm === 'number_of_month' || dm === 'monthly' || dm === 'by_month' || dm === 'month') {
        return true
      }
    }

    // косвенные признаки
    if ((typeof ev.month_year === 'number') && (typeof ev.month_number === 'number')) {
      return true
    }
  }

  return false
}

/**
 * Возвращает кортеж: [monthly[], regular[]]
 * - monthly: только те, которые относятся к выбранному месяцу/году
 * - regular: всё остальное
 */
function splitMonthlyForPeriod(items, year, month) {
  const monthly = []
  const regular = []

  for (let i = 0; i < items.length; i++) {
    const it = items[i]
    if (!isMonthlyEvent(it)) {
      regular.push(it)
      continue
    }

    // Фильтрация по периоду: сначала пробуем явные поля
    const ev = it.event || {}
    const y = typeof ev.month_year === 'number' ? ev.month_year : null
    const m = typeof ev.month_number === 'number' ? ev.month_number : null

    let isForPeriod = false
    if (y !== null && m !== null) {
      isForPeriod = (y === year && m === month)
    } else {
      // fallback: проверим datetime/starts_at попадание в (year, month)
      // Нам важно НЕ подвязывать к конкретному дню, но понимать месяц
      let iso = null
      if (typeof it.datetime === 'string' && it.datetime) iso = it.datetime
      else if (ev && typeof ev.starts_at === 'string' && ev.starts_at) iso = ev.starts_at

      if (iso) {
        const d = new Date(iso)
        if (!isNaN(d.getTime())) {
          isForPeriod = (d.getFullYear() === year && (d.getMonth() + 1) === month)
        }
      }
    }

    if (isForPeriod) monthly.push(it)
    else {
      // это месячное, но не наш период — игнорируем; в regular не кладём
    }
  }

  return [monthly, regular]
}

function buildPatternText(arr) {
  if (!Array.isArray(arr) || arr.length === 0) return 'Не задано'

  const parts = []
  for (let i = 0; i < arr.length; i++) {
    const n = arr[i]
    if (typeof n !== 'number' || n <= 0) continue

    const isWork = (i % 2 === 0) // 0,2,4... рабочие; 1,3,5... выходные
    const dayWord = (n === 1) ? 'день' : 'дней'

    if (isWork) parts.push(String(n) + ' рабочих ' + dayWord)
    else parts.push(String(n) + ' выходных ' + dayWord)
  }

  if (parts.length === 0) return 'Не задано'
  return parts.join(', потом ')
}

const patternText = computed(() => {
  const p = pattern.value
  if (!p || typeof p !== 'object') return 'Не задано'

  const arr = p.pattern_after_start
  return buildPatternText(arr)
})

function openTemplatePicker() {
  // следующий шаг: открыть вторую секцию/диалог выбора шаблона
  console.log('TODO: template picker')
}


function buildTempSchedule(year, month) {
  // Сколько дней в месяце
  const daysInMonth = new Date(year, month, 0).getDate()

  const ruWeekdays = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
  const todayDate = new Date()
  const todayY = todayDate.getFullYear()
  const todayM = todayDate.getMonth() + 1
  const todayD = todayDate.getDate()

  // 1–5: off; далее цикл 2 work / 2 off
  const tempDays = []
  for (let d = 1; d <= daysInMonth; d++) {
    const jsDate = new Date(year, month - 1, d)
    const wd = ruWeekdays[jsDate.getDay()]

    let type
    if (d <= 5) {
      type = 'off'
    } else {
      const idx = (d - 6) % 4 // 0,1 -> work; 2,3 -> off
      if (idx === 0 || idx === 1) type = 'work'
      else type = 'off'
    }

    const dateStr = String(year) + '-' + String(month).padStart(2, '0') + '-' + String(d).padStart(2, '0')

    tempDays.push({
      date: dateStr,
      day: d,
      weekday: wd,
      is_today: (year === todayY && month === todayM && d === todayD),
      group_id: null,
      overrides: [],
      notes: '',
      type: type,
      forced: false
    })
  }

  // Последний день — принудительно рабочий, если он off
  if (tempDays.length > 0 && tempDays[tempDays.length - 1].type === 'off') {
    tempDays[tempDays.length - 1].type = 'work'
    tempDays[tempDays.length - 1].forced = true
  }

  // Группы: 5, 4, 4, 4, ...
  const tempGroups = []
  let i = 0
  let first = true
  while (i < tempDays.length) {
    const chunkSize = first ? 5 : 4
    const chunk = tempDays.slice(i, i + chunkSize)
    if (chunk.length === 0) break
    tempGroups.push(chunk)
    i += chunkSize
    first = false
  }

  // Паттерн (число часов в день — number)
  const tempPattern = {
    id: -1,
    name: 'TEMP-OVERRIDE',
    description: '5 off → 2/2, last forced work',
    mode: 'custom',
    weekday_map: null,
    days_off_at_start: 5,
    pattern_after_start: [2, 2],
    last_day_always_working: true,
    working_day_duration: 5,
    cycle_length: 4
  }

  return { days: tempDays, groups: tempGroups, pattern: tempPattern }
}

// --- HELPERS ---
const disabledDate = function () { return false }

const monthlyEvents = ref([])

function handleEditMonthly(ev){
  // ev — это уже вложенный event (мы его передаём из компонента)
  currentTask.value = ev
  isModalVisible.value = true
}

async function handleRemoveMonthly(ev){
  try {
    if (!ev || !ev.id) return
    await axios.delete('schedule/events/' + ev.id + '/delete/')
    await loadAllEvents(selectedYear.value, selectedMonth.value)
  } catch (err) {
    console.error('Ошибка при удалении месячного события:', err)
  }
}


function onWheel(e) {
  const container = scrollContainer.value
  if (!container) return
  if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
    container.scrollLeft += e.deltaY
  } else {
    container.scrollLeft += e.deltaX
  }
}

function toLocalDateKey(dateObj) {
  if (!(dateObj instanceof Date) || isNaN(dateObj.getTime())) {
    return 'invalid-date'
  }
  const y = dateObj.getFullYear()
  const m = String(dateObj.getMonth() + 1).padStart(2, '0')
  const d = String(dateObj.getDate()).padStart(2, '0')
  return y + '-' + m + '-' + d
}

function isCancelledTask(item) {
  if (!item) return false

  if (item.overlay && typeof item.overlay.status === 'string') {
    const s = item.overlay.status.toLowerCase()
    if (s === 'cancelled') return true
  }

  const candidates = []
  if (typeof item.status === 'string') candidates.push(item.status)
  if (typeof item.instance_status === 'string') candidates.push(item.instance_status)
  if (typeof item.state === 'string') candidates.push(item.state)
  if (item.event && typeof item.event.status === 'string') candidates.push(item.event.status)

  for (let i = 0; i < candidates.length; i++) {
    const v = candidates[i]
    if (typeof v === 'string' && v.toLowerCase() === 'cancelled') return true
  }

  if (item.is_cancelled === true) return true
  return false
}

// Нормализатор событий: гарантируем валидную ISO-дату в .datetime
function normalizeEvent(e) {
  if (!e || typeof e !== 'object') return null

  let iso = e.datetime
  if ((!iso || typeof iso !== 'string' || iso.length === 0) && e.event && typeof e.event.starts_at === 'string') {
    iso = e.event.starts_at
  }
  if (!iso || typeof iso !== 'string') return null

  const d = new Date(iso)
  if (isNaN(d.getTime())) {
    console.warn('[all_events] invalid date', { id: e.id, source_event_id: e.source_event_id, iso: iso })
    return null
  }
  return Object.assign({}, e, { datetime: d.toISOString() })
}

// --- TASK MODAL ---
function handleEditTask(task) {
  currentTask.value = task.event
  isModalVisible.value = true
}
async function closeModal() {
  isModalVisible.value = false
  currentTask.value = null
  await loadAllEvents(selectedYear.value, selectedMonth.value)
}

// --- TASK ACTIONS ---
const handleCompleteTask = async function (task, newStatus) {
  try {
    const payload = {
      status: newStatus ? 'complete' : 'incomplete',
      is_completed: newStatus,
      instance_datetime: task.datetime
    }
    if (task.is_recurring) {
      await axios.patch('schedule/events/' + task.event.id + '/update-status/', payload)
    } else {
      await axios.patch('schedule/events/' + task.event.id + '/', {
        is_completed: newStatus,
        status: payload.status
      })
    }
    await loadAllEvents(selectedYear.value, selectedMonth.value)
  } catch (err) {
    console.error('Не удалось обновить статус:', err)
  }
}

const handleRemoveTask = async function (task) {
  try {
    if (task.is_recurring) {
      await axios.delete('schedule/events/' + task.event.id + '/delete/', {
        params: { instance_datetime: task.datetime }
      })
    } else {
      await axios.delete('schedule/events/' + task.event.id + '/delete/')
    }
    await loadAllEvents(selectedYear.value, selectedMonth.value)
  } catch (err) {
    console.error('Ошибка при удалении задачи:', err)
  }
}

const handleAddTask = async function () {
  try {
    await loadAllEvents(selectedYear.value, selectedMonth.value)
  } catch (err) {
    console.error('Ошибка при добавлении задачи:', err)
  }
}

// --- DATE/USER SYNC ---
watch(selectedDate, function (date) {
  if (date instanceof Date) {
    selectedYear.value = date.getFullYear()
    selectedMonth.value = date.getMonth() + 1
  }
})
watch([selectedYear, selectedMonth], function ([year, month]) {
  if (year && month) {
    selectedDate.value = new Date(year, month - 1)
  }
})

// --- FILTERED/COUNTS/GROUPS ---
const filteredDays = computed(function () {
  let list = days.value.slice()

  if (doNotShowPast.value) {
    const todayLocal = new Date()
    const todayOnly = new Date(
        todayLocal.getFullYear(),
        todayLocal.getMonth(),
        todayLocal.getDate()
    )
    list = list.filter(function (d) {
      const dd = parseISO(d.date)
      const ddOnly = new Date(dd.getFullYear(), dd.getMonth(), dd.getDate())
      return ddOnly >= todayOnly
    })
  }

  if (showDays.value !== 'all') {
    list = list.filter(function (d) { return d.type === showDays.value })
  }

  if (showScope.value === 'week') {
    const currentWeek = getISOWeek(new Date())
    list = list.filter(function (d) {
      return getISOWeek(parseISO(d.date)) === currentWeek
    })
  }

  return list
})


// 🧩 Группы из API + фильтрация по allowedDates
const groupedFilteredDays = computed(function () {
  const allowedDates = new Set()
  for (let i = 0; i < filteredDays.value.length; i++) {
    const d = filteredDays.value[i]
    if (d && typeof d.date === 'string') {
      allowedDates.add(d.date)
    }
  }

  const result = []
  if (Array.isArray(groups.value)) {
    for (let gi = 0; gi < groups.value.length; gi++) {
      const group = groups.value[gi]
      if (Array.isArray(group)) {
        const kept = []
        for (let di = 0; di < group.length; di++) {
          const day = group[di]
          if (day && typeof day.date === 'string' && allowedDates.has(day.date)) {
            kept.push(day)
          }
        }
        if (kept.length > 0) result.push(kept)
      }
    }
  }
  return result
})

// --- USER ROLES / SELECT OPTIONS ---
const isManager = computed(function () {
  const user = currentUser.value
  if (!user) return false

  if (typeof user.is_manager === 'boolean') return user.is_manager

  const roleCandidates = []
  if (typeof user.role === 'string') roleCandidates.push(user.role)
  if (Array.isArray(user.roles)) {
    for (let i = 0; i < user.roles.length; i++) roleCandidates.push(user.roles[i])
  }
  if (Array.isArray(user.role)) {
    for (let i = 0; i < user.role.length; i++) roleCandidates.push(user.role[i])
  }
  if (Array.isArray(user.groups)) {
    for (let i = 0; i < user.groups.length; i++) {
      const group = user.groups[i]
      if (typeof group === 'string') roleCandidates.push(group)
      else if (group && typeof group.name === 'string') roleCandidates.push(group.name)
    }
  }
  for (let i = 0; i < roleCandidates.length; i++) {
    const r = roleCandidates[i]
    if (typeof r === 'string' && r.toLowerCase().indexOf('manager') !== -1) return true
  }
  return false
})

const showUserSelector = computed(function () {
  return isManager.value
})

const usersLoadedFromApi = ref(false)

function logCurrentUserAccess() {
  console.log('Текущая информация о пользователе:', currentUser.value)
  if (isManager.value) console.log('Текущий пользователь менеджер')
  else console.log('Текущий пользователь не менеджер')
}

watch([currentUser, isManager], function () {
  logCurrentUserAccess()
}, { immediate: true })

// 🔓 Разблокировка селекта для менеджера
watch(isManager, function (canManage) {
  userSelectorLocked.value = !canManage
}, { immediate: true })

function mergeUserOptions(candidates) {
  if (!Array.isArray(candidates)) return
  const map = new Map()
  for (let i = 0; i < userOptions.value.length; i++) {
    const u = userOptions.value[i]
    map.set(u.id, u)
  }
  for (let i = 0; i < candidates.length; i++) {
    const c = candidates[i]
    if (!c || typeof c !== 'object') continue
    const id = c.id
    if (id === undefined || id === null) continue
    const prev = map.get(id) || {}
    map.set(id, Object.assign({}, prev, c))
  }
  userOptions.value = Array.from(map.values())
}

async function loadUserOptions() {
  if (usersLoadedFromApi.value) return
  try {
    console.log('сейчас будем брать юзеров')
    const res = await axios.get('identity/users_unsafe/')
    const dataPayload = res.data
    let payload = dataPayload
    if (dataPayload && Array.isArray(dataPayload.results)) {
      payload = dataPayload.results
    }
    if (Array.isArray(payload)) mergeUserOptions(payload)
  } catch (err) {
    console.warn('Не удалось загрузить полный список пользователей, используем fallback из расписаний', err)
  } finally {
    usersLoadedFromApi.value = true
  }
}

watch(currentUser, function (user) {
  if (!user || !user.id) return
  if (isManager.value) {
    mergeUserOptions([user])
    if (!selectedUser.value) selectedUser.value = user.id
  } else {
    userOptions.value = [user]
    selectedUser.value = user.id
  }
}, { immediate: true })

watch(isManager, async function (canManage) {
  if (canManage) {
    await loadUserOptions()
    if (currentUser.value && currentUser.value.id && !selectedUser.value) {
      selectedUser.value = currentUser.value.id
    }
  } else if (currentUser.value) {
    userOptions.value = [currentUser.value]
    selectedUser.value = currentUser.value.id
  }
}, { immediate: true })

watch([isManager, currentUser, selectedUser], function ([manager, user, selected]) {
  if (!manager && user && user.id && selected !== user.id) {
    selectedUser.value = user.id
  }
})

// --- DATA LOADING ---
onMounted(async () => {
  try {
    const res = await axios.get('schedule/month-schedules/')
    const data = res.data

    const years = new Set()
    const months = new Set()
    const usersMap = new Map()

    for (let i = 0; i < data.length; i++) {
      const item = data[i]
      years.add(item.year)
      months.add(item.month)
      if (item.user && !usersMap.has(item.user.id)) usersMap.set(item.user.id, item.user)
    }

    availableYears.value = Array.from(years).sort()
    availableMonths.value = Array.from(months).sort(function (a, b) { return a - b })

    const fallbackUsers = Array.from(usersMap.values())
    if (fallbackUsers.length) mergeUserOptions(fallbackUsers)
  } catch (err) {
    ElMessage.error('Не удалось загрузить доступные данные 🥲')
    console.error(err)
  }
})

async function loadAllEvents(year, month) {
  // 🔕 Пока оверрайд включён — полностью игнорируем таски
  if (USE_TEMP_OVERRIDE) {
    tasks.value = {}
    return
  }

  loading.value = true
  try {
    const res = await axios.get('schedule/all_events/?year=' + year + '&month=' + month)
    const raw = res.data

    let payloadEvents = []
    if (Array.isArray(raw)) {
      payloadEvents = raw
    } else if (raw && Array.isArray(raw.events)) {
      payloadEvents = raw.events
    }

    const meta = raw && raw.meta ? raw.meta : null
    console.log('[all_events] meta:', meta)
    console.log('[all_events] count(raw):', payloadEvents.length)

    for (let i = 0; i < payloadEvents.length; i++) {
      const e = payloadEvents[i]
      const rawIso = (e && typeof e.datetime === 'string' && e.datetime.length > 0)
          ? e.datetime
          : (e && e.event && typeof e.event.starts_at === 'string' ? e.event.starts_at : null)
      if (!rawIso) {
        console.warn('[all_events] missing datetime for', { id: e ? e.id : null, source_event_id: e ? e.source_event_id : null })
      } else {
        const d = new Date(rawIso)
        if (isNaN(d.getTime())) {
          console.warn('[all_events] unparsable date', { id: e ? e.id : null, rawIso: rawIso })
        }
      }
    }

    const normalized = []
    for (let i = 0; i < payloadEvents.length; i++) {
      const ne = normalizeEvent(payloadEvents[i])
      if (ne) normalized.push(ne)
    }
    console.log('[all_events] count(normalized):', normalized.length)


    const [monthly, regular] = splitMonthlyForPeriod(normalized, year, month)
    monthlyEvents.value = monthly

/*    const visible = []
    for (let i = 0; i < normalized.length; i++) {
      const item = normalized[i]
      if (showCancelled.value || !isCancelledTask(item)) {
        visible.push(item)
      }
    }*/

    const visible = []
    for (let i = 0; i < regular.length; i++) {
      const item = regular[i]
      if (showCancelled.value || !isCancelledTask(item)) {
        visible.push(item)
      }
    }

    const tasksByDate = {}
    for (let i = 0; i < visible.length; i++) {
      const dt = new Date(visible[i].datetime)
      const dateKey = toLocalDateKey(dt)
      if (!tasksByDate[dateKey]) tasksByDate[dateKey] = []
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
watch([selectedUser, selectedMonth, selectedYear], async function ([user, month, year]) {
  if (!user || !month || !year) return
  loading.value = true
  try {
    const res = await axios.get('schedule/preview?year=' + year + '&month=' + month + '&user=' + user)
    const data = res.data

    days.value = data && Array.isArray(data.days) ? data.days : []
    groups.value = data && Array.isArray(data.groups) ? data.groups : []
    pattern.value = data && data.pattern ? data.pattern : {}
    tasks.value = (data && typeof data.tasks === 'object' && data.tasks !== null) ? data.tasks : {}
    summary.value = (data && typeof data.summary === 'object') ? data.summary : null

    console.log('[preview] days:', Array.isArray(days.value) ? days.value.length : 0)
    console.log('[preview] groups:', Array.isArray(groups.value) ? groups.value.length : 0)

    // --- 🔥 Временная подмена на требуемую схему ---
    if (USE_TEMP_OVERRIDE) {
      const built = buildTempSchedule(year, month)
      days.value = built.days
      groups.value = built.groups
      pattern.value = built.pattern
      tasks.value = {} // не рисуем all_events
      summary.value = computeSummaryFromDays(built.days, built.pattern)
      await nextTick()
      return // не зовём loadAllEvents
    }

    // выкидываем cancelled из tasks (если пришли из /preview)
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
            const statusStr = (t && typeof t.status === 'string') ? t.status : ''
            if (showCancelled.value || statusStr !== 'cancelled') {
              kept.push(t)
            }
          }
          if (kept.length > 0) cleaned[k] = kept
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


function computeSummaryFromDays(daysArr, patternObj) {
  const counts = { work: 0, off: 0, holiday: 0, sick: 0, other: 0 }
  for (let i = 0; i < daysArr.length; i++) {
    const t = daysArr[i] && daysArr[i].type ? String(daysArr[i].type) : ''
    if (t === 'work') counts.work++
    else if (t === 'off') counts.off++
    else if (t === 'holiday') counts.holiday++
    else if (t === 'sick') counts.sick++
    else counts.other++
  }
  const hoursPerDay =
      (patternObj && typeof patternObj.working_day_duration === 'number')
          ? patternObj.working_day_duration
          : 8
  return {
    work_days: counts.work,
    off_days: counts.off,
    holidays: counts.holiday,
    sick_days: counts.sick,
    hours_per_day: hoursPerDay,
    work_hours_total: counts.work * hoursPerDay,
    total_days: daysArr.length,
    other_days: counts.other,
  }
}

const isScheduleDialogOpen = ref(false)

const editForm = ref({
  template: '',
  daysOffAtStart: 0,
  lastDayWorking: true
})

function openScheduleDialog() {
  const p = pattern.value

  const hasPattern = p && typeof p === 'object' && Object.keys(p).length > 0
  const hasId = hasPattern && (p.id !== undefined && p.id !== null)

  if (!hasPattern || !hasId) {
    ElMessage.warning('Расписание ещё загружается — попробуй через секунду')
    return
  }

  // заполняем форму из текущего паттерна (из /schedule/preview)
  editForm.value = {
    template: (typeof p.mode === 'string' && p.mode) ? p.mode : '',
    daysOffAtStart: (typeof p.days_off_at_start === 'number') ? p.days_off_at_start : 0,
    lastDayWorking: (typeof p.last_day_always_working === 'boolean') ? p.last_day_always_working : true
  }

  isScheduleDialogOpen.value = true
}


function closeScheduleDialog() {
  isScheduleDialogOpen.value = false
}

const scheduleSummary = computed(() => {
  // временно: чтобы было что показать
  if (editForm.value.template) {
    return editForm.value.template
  }
  return 'Не задано'
})

async function saveSchedule() {
  try {
    const payload = {
      template: editForm.value.template,
      days_off_at_start: editForm.value.daysOffAtStart,
      last_day_working: editForm.value.lastDayWorking
    }

    // endpoint подставишь реальный (пока заглушка)
    await axios.post('schedule/month-pattern/', payload)

    isScheduleDialogOpen.value = false
  } catch (err) {
    console.error('Ошибка при сохранении расписания:', err)
  }
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

.month-overview {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  gap: 1.5rem;
  flex-wrap: nowrap;
  padding: 1rem 30vw; /* если понравилось затемнение по краям, можно оставить */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE 10+ */
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

.month-right {
  flex: 0 0 320px; /* ширина панели, можно подправить по вкусу */
  max-height: 70vh;
  overflow-y: auto;
  padding-left: 1rem;
  border-left: 1px solid var(--el-border-color-lighter);
  box-sizing: border-box;
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

/* 🔶 Подсветка форсированного рабочего дня */
.forced-day {
  outline: 2px dashed var(--el-color-warning);
  outline-offset: 3px;
  border-radius: 8px;
}

.month-main {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
}

.month-body {
  max-width: 90vw;
  margin: 0 auto;
}

.month-scroll {
  position: relative;
  scroll-behavior: smooth;
  mask-image: linear-gradient(to right, transparent, black 7%, black 93%, transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, black 7%, black 93%, transparent);
  overflow-x: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE 10+ */
}

</style>

<style scoped lang="scss">
.month-summary-clickzone {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;

  padding: 14px 18px;
  border-radius: 14px;

  cursor: pointer;
  user-select: none;

  transition: background-color 0.15s ease, box-shadow 0.15s ease, transform 0.08s ease;
}

.month-summary-clickzone:hover {
  background-color: rgba(64, 158, 255, 0.08);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
}

.month-summary-clickzone:active {
  transform: translateY(1px);
}

.month-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.schedule-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.schedule-subtitle {
  margin-top: -1rem;

}


.schedule-section-title {
  font-weight: 600;
  margin-top: 0px;
}

.kv {
  display: grid;
  grid-template-columns: 110px 1fr;
  gap: 10px;
  padding: 6px 0;
}

.k {
  opacity: 0.7;
}
</style>


<style>
.content-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
