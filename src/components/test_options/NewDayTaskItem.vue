<template>
  <div
      class="day-task-item"
      :class="{ cancelled: isCancelled(task) }"
  >
    <!-- Контекстное меню по правому клику -->
    <el-dropdown
        trigger="contextmenu"
        @command="(cmd) => onDropdown(cmd)"
    >
      <div class="row">
        <!-- 1) Время -->
        <span
            v-if="hasTime"
            class="time-dim"
        >
          {{ timeHM }}
        </span>

        <!-- 2) Мини-чекбокс + название события -->
        <el-checkbox
            class="mini-checkbox"
            :model-value="isCompleted(task)"
            :label="eventTitle"
            :title="checkboxTitle"
            @change="(val) => onToggle(val)"
            :aria-label="eventTitle"
        />

        <!-- 3) Сумма справа -->
        <div
            class="amount-wrap"
            v-if="hasAmount"
        >
          <AmountNumber
              class="amount-dim"
              :amount="toNumber(ev && ev.amount)"
          />
        </div>
      </div>

      <!-- Комментарий: скрыт, показывается при hover -->
      <div
          class="comment"
          v-if="hasDescription"
      >
        {{ eventDescription }}
      </div>

      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="edit">Редактировать</el-dropdown-item>
          <el-dropdown-item command="delete">Удалить</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AmountNumber from './AmountNumber.vue'

const props = defineProps({
  task: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['completeTask', 'editTask', 'removeTask'])

// ---------- безопасные геттеры ----------
function getOverlay (t) {
  if (!t) return null
  if ('overlay' in t) return t.overlay
  return null
}

function getEvent (t) {
  if (!t) return null
  if ('event' in t) return t.event
  return null
}

const ev = computed(() => getEvent(props.task))

function isCancelled (t) {
  const ov = getOverlay(t)
  if (!ov) return false
  return 'status' in ov && ov.status === 'cancelled'
}

function isCompleted (t) {
  const ov = getOverlay(t)
  if (ov && 'is_completed' in ov) {
    return !!ov.is_completed
  }
  const ev = getEvent(t)
  if (!ev) return false
  if ('is_completed' in ev) return !!ev.is_completed
  return false
}

function toNumber (v) {
  if (v === null || typeof v === 'undefined') return null
  if (typeof v === 'string') {
    const n = Number(v)
    return Number.isFinite(n) ? n : null
  }
  if (typeof v === 'number') {
    return Number.isFinite(v) ? v : null
  }
  return null
}

// ---------- вычисления ----------
const eventTitle = computed(() => {
  const ev = getEvent(props.task)
  if (!ev) return 'Без названия'
  if ('name' in ev && typeof ev.name === 'string' && ev.name.trim().length > 0) {
    return ev.name
  }
  return 'Без названия'
})

const eventDescription = computed(() => {
  const ev = getEvent(props.task)
  if (!ev || typeof ev.description !== 'string') return ''
  return ev.description
})

const hasAmount = computed(() => {
  const ev = getEvent(props.task)
  if (!ev) return false
  const n = toNumber(ev.amount)
  return n !== null
})

const hasDescription = computed(() => {
  const ev = getEvent(props.task)
  if (!ev) return false
  return typeof ev.description === 'string' && ev.description.trim().length > 0
})

const checkboxTitle = computed(() => eventTitle.value)

// ---------- эмиты действий ----------
function onToggle (isChecked) {
  emit('completeTask', props.task, isChecked)
}

function onDropdown (cmd) {
  if (cmd === 'edit') emit('editTask', props.task)
  else if (cmd === 'delete') emit('removeTask', props.task)
}

// ----- время внутри карточки -----
function getEventStartISO (t) {
  const ev = getEvent(t)
  if (!ev) return null

  let iso = null
  if ('start_datetime' in ev && ev.start_datetime) iso = ev.start_datetime
  else if ('starts_at' in ev && ev.starts_at) iso = ev.starts_at
  else if ('start' in ev && ev.start) iso = ev.start

  if (!iso || typeof iso !== 'string') return null
  const trimmed = iso.trim()
  return trimmed.length > 0 ? trimmed : null
}

function parseDate (iso) {
  if (!iso) return null
  const d = new Date(iso)
  if (isNaN(d.getTime())) return null
  return d
}

function formatHM (d) {
  if (!d) return ''
  const h = d.getHours()
  const m = d.getMinutes()
  const hh = h < 10 ? '0' + h : String(h)
  const mm = m < 10 ? '0' + m : String(m)
  return hh + ':' + mm
}

const timeHM = computed(() => {
  const iso = getEventStartISO(props.task)
  const d = parseDate(iso)
  return formatHM(d)
})

const hasTime = computed(() => {
  const s = timeHM.value
  return typeof s === 'string' && s.length > 0
})
</script>

<style scoped>
.day-task-item {
  padding: 6px 8px;
  border-radius: 10px;
  transition: background-color 0.15s ease, opacity 0.15s ease;
}

.day-task-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

/* отменённые — полупрозрачные */
.cancelled {
  opacity: 0.45;
}

/* строка */
.row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  align-content: center;
  flex-direction: row;
  flex-wrap: nowrap;
}

/* мини-чекбокс и заголовок */
.mini-checkbox {
  padding: 0px;
  display: flex;
  align-items: center;
  margin-left: 0px !important;
  margin-right: 0px !important;
}

.mini-checkbox :deep(.el-checkbox__inner) {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  transform: translateY(-1px);

}

.mini-checkbox :deep(.el-checkbox__label) {
  font-weight: 500; /* акцент на названии события */
  color: #222;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  line-height: 1.2;
  margin-top: 0px !important;
}

/* сумма — справа */
.amount-wrap {
  margin-left: auto;
  flex: 0 0 auto;
}

.amount-dim {
  opacity: 0.4;
  font-size: 0.9rem;
  white-space: nowrap;
}

/* комментарий появляется при hover */
.comment {
  margin-left: 26px;
  color: #666;
  font-size: 0.9rem;
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition: opacity 0.15s ease, max-height 0.15s ease;
  will-change: opacity, max-height;
}

.day-task-item:hover .comment {
  max-height: 160px;
  opacity: 0.8;
}

/* Время — менее важное: мелко и серо */
.time-dim {
  font-size: 0.85rem;
  color: #999;
  white-space: nowrap;
  margin-right: 12px; /* 🔹 увеличиваем расстояние между временем и чекбоксом */
}

.mini-checkbox {
  padding: 0 !important;
  margin: 0 !important;
  display: flex !important;
  align-items: center !important;
  line-height: 1 !important;
}

/* Сбрасываем кривые внутренние отступы Element Plus */
.mini-checkbox :deep(.el-checkbox__input) {
  margin: 0 !important;
  padding: 0 !important;
}

/* Контейнер чекбокса */
.mini-checkbox :deep(.el-checkbox__inner) {
  width: 14px !important;
  height: 14px !important;
  border-radius: 4px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* Убираем влияние внутренних псевдоэлементов */
.mini-checkbox :deep(.el-checkbox__inner::before),
.mini-checkbox :deep(.el-checkbox__inner::after) {
  margin: 0 !important;
  padding: 0 !important;
}

.mini-checkbox :deep(.el-checkbox__label) {
  display: flex !important;
  align-items: center !important;
  line-height: 1.1 !important;
  margin-left: -4px !important; /* 🔹 было 6 — прижали текст ближе к квадратику */
}

</style>
