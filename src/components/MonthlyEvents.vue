<template>
  <div class="monthly-block">
    <h3 class="monthly-title">Месячные события</h3>

    <div
        class="monthly-list"
        v-if="events && events.length"
    >
      <div
          class="monthly-card"
          v-for="item in events"
          :key="cardKey(item)"
          :class="{ 'monthly-card--done': isDone(item) }"
      >
        <div class="card-row">
          <!-- чекбокс выполнения (пока только фронтовый визуал) -->
          <el-checkbox
              class="monthly-checkbox"
              :model-value="isDone(item)"
              @change="() => toggleDone(item)"
              :aria-label="titleOf(item)"
          />

          <div
              class="title"
              :title="titleOf(item)"
          >
            {{ titleOf(item) }}
          </div>

          <div
              class="amount"
              v-if="hasAmount(item)"
          >
            <AmountNumber
                class="dim"
                :amount="toNumber(amountOf(item))"
            />
          </div>
        </div>

        <div
            class="desc"
            v-if="hasDesc(item)"
        >
          {{ descOf(item) }}
        </div>
      </div>
    </div>

    <div
        class="empty"
        v-else
    >
      Нет месячных событий
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AmountNumber from './AmountNumber.vue'

const props = defineProps({
  events: { type: Array, default: () => [] }
})

const emit = defineEmits(['edit', 'remove'])

/**
 * Локальное хранилище "выполненности" — пока только визуальный эффект на фронте.
 * Потом можно будет заменить на реальные данные из бэка.
 */
const doneIds = ref(new Set())

function getEvent (obj) {
  if (!obj) return null
  if ('event' in obj) return obj.event
  return obj
}

function getId (obj) {
  const raw = obj && (obj.id || (obj.event && obj.event.id))
  if (!raw) return null
  return String(raw)
}

function cardKey (obj) {
  const id = getId(obj)
  if (id !== null && typeof id !== 'undefined') {
    return id
  }
  // запасной вариант, если совсем нет id
  return JSON.stringify(obj) + String(Math.random())
}

function titleOf (obj) {
  const ev = getEvent(obj)
  if (!ev) return 'Без названия'
  if (typeof ev.name === 'string' && ev.name.trim().length > 0) return ev.name
  return 'Без названия'
}

function descOf (obj) {
  const ev = getEvent(obj)
  if (!ev) return ''
  if (typeof ev.description === 'string') return ev.description
  return ''
}

function hasDesc (obj) {
  const t = descOf(obj)
  return typeof t === 'string' && t.trim().length > 0
}

function amountOf (obj) {
  const ev = getEvent(obj)
  if (!ev) return null
  return ev.amount
}

function toNumber (v) {
  if (v === null || typeof v === 'undefined') return null
  if (typeof v === 'string') {
    const n = Number(v)
    return Number.isFinite(n) ? n : null
  }
  if (typeof v === 'number') return Number.isFinite(v) ? v : null
  return null
}

function hasAmount (obj) {
  const n = toNumber(amountOf(obj))
  return n !== null
}

/* визуальная выполненность */
function isDone (obj) {
  const id = getId(obj)
  if (!id) return false
  return doneIds.value.has(id)
}

function toggleDone (obj) {
  const id = getId(obj)
  if (!id) return
  const next = new Set(doneIds.value)
  if (next.has(id)) {
    next.delete(id)
  } else {
    next.add(id)
  }
  doneIds.value = next
}

/* пока не используем, но пусть останутся для будущего */
function emitEdit (obj) { emit('edit', getEvent(obj)) }
function emitRemove (obj) { emit('remove', getEvent(obj)) }
</script>

<style scoped>
.monthly-block {
  margin: 8px 0 4px;
  padding: 0;
  max-width: 380px; /* аккуратная вертикальная панель */
}

/* заголовок должен быть чуть значимее, чем строки */
.monthly-title {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  text-align: left;
  color: #555;
}

/* вертикальный список карточек */
.monthly-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* карточка: плоская, без ощущения кнопки */
.monthly-card {
  border-radius: 10px;
  padding: 6px 10px;

  border: 1px solid rgba(0, 0, 0, 0.04);
  background: rgba(255, 255, 255, 0.85);

  box-shadow: none;
  transition:
      background-color 0.15s ease,
      border-color 0.15s ease,
      transform 0.1s ease;
}

/* лёгкий hover без "кнопочности" */
.monthly-card:hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(0, 0, 0, 0.08);
}

/* состояние "выполнено" — немного бледнее */
.monthly-card--done {
  opacity: 0.6;
}

/* верхняя строка: чекбокс + название + сумма */
.card-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* чекбокс — аккуратный и компактный */
.monthly-checkbox {
  padding: 0 !important;
  margin: 0 !important;
  display: flex !important;
  align-items: center !important;
  line-height: 1 !important;
}

.monthly-checkbox :deep(.el-checkbox__input) {
  margin: 0 !important;
  padding: 0 !important;
}

.monthly-checkbox :deep(.el-checkbox__inner) {
  width: 14px !important;
  height: 14px !important;
  border-radius: 4px !important;
  margin: 0 !important;
  padding: 0 !important;
}

.monthly-checkbox :deep(.el-checkbox__label) {
  display: none !important; /* текст мы выводим отдельно в .title */
}

/* название события */
.title {
  font-weight: 500;
  color: #222;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
  flex: 1 1 auto;
}

/* сумма — справа, спокойная */
.amount {
  flex: 0 0 auto;
}

.amount .dim {
  opacity: 0.6;
  font-size: 0.88rem;
}

/* описание — маленький второстепенный текст */
.desc {
  margin-top: 3px;
  color: #666;
  font-size: 0.8rem;
}

/* пустое состояние */
.empty {
  opacity: 0.6;
  padding: 4px 0;
  font-size: 0.85rem;
}
</style>
