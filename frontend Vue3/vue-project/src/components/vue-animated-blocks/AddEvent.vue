<template>
  <div class="page-wrapper">
    <div class="event-form-container">
      <h2 class="form-title">Создание события</h2>

      <el-radio-group
          v-model="pendingType"
          class="event-type-group"
          @change="handleEventTypeChange"
      >
        <el-radio label="once">Одноразовое</el-radio>
        <el-radio label="recurring">Повторяемое</el-radio>
        <el-radio label="income">Приход денег</el-radio>
      </el-radio-group>

      <transition name="fade-slide">
        <div v-if="eventType" :key="eventType" class="form-section">
          <el-input v-model="form.name" placeholder="Название события" class="input-field" />
          <el-input type="textarea" v-model="form.comment" placeholder="Комментарий (опционально)" rows="3" class="input-field" />
          <el-switch v-model="form.isActive" active-text="Активно" inactive-text="Не активно" />

          <ExpandTransition :visible="eventType === 'once'">
            <el-date-picker v-model="form.date" type="date" placeholder="Дата события" class="input-field" />
          </ExpandTransition>

          <ExpandTransition :visible="eventType === 'recurring'">
            <div class="block-section">
              <RecurringBlock :form="form" />
            </div>
          </ExpandTransition>

          <ExpandTransition :visible="true">
            <div class="block-section">
              <FinancialBlock :form="form" />
            </div>
          </ExpandTransition>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FinancialBlock from './FinancialBlock.vue'
import RecurringBlock from './RecurringBlock.vue'
import ExpandTransition from './ExpandTransition.vue'

const eventType = ref('')
const pendingType = ref('')

const form = ref({
  name: '',
  comment: '',
  isActive: true,
  currency: 'RUB',
  amountRub: null,
  foreignAmount: null,
  recurrenceRule: null,
  date: '',
  dateStart: '',
  dateEnd: '',
  isFinancialEvent: false,
})

function handleEventTypeChange(newType) {
  if (eventType.value) {
    eventType.value = ''
    setTimeout(() => {
      eventType.value = newType
    }, 450)
  } else {
    eventType.value = newType
  }
}
</script>

<style scoped>
.page-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0;
  background-color: var(--bg-main);
  height: 85vh;
}

.event-form-container {
  width: 100%;
  max-width: 640px;
  min-width: 640px;
  background-color: var(--bg-secondary);
  padding: 2rem;
  border-radius: var(--radius-card);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
  overflow-y: auto;
  transition: all 0.3s ease;
  height: 100%;
  min-height: 100%;
  position: relative;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.event-form-container::-webkit-scrollbar {
  display: none;
}

.block-section {
  background-color: var(--bg-main);
  border-radius: 0;
  border-radius: var(--radius-card);
  /* box-shadow: 0 0 8px rgba(0, 0, 0, 0.2); /* мягкое внешнее свечение */
  box-shadow: 0 -4px 6px rgba(0,0,0,0.05);
  margin: 2rem -1.5rem 0rem;
  padding: 0 1rem; /* или любое своё */
}

.form-title {
  text-align: center;
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 2rem;
  color: var(--text-main);
}

.event-type-group {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.form-section {
  background: var(--bg-main);
  padding: 1.5rem;
  border-radius: var(--radius-card);
  margin-bottom: 0rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.5s ease;
}

.input-field {
  margin-bottom: 1rem;
}

/* Анимация */
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.5s ease;
}

.fade-slide-enter-from, .fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-slide-enter-to, .fade-slide-leave-from {
  opacity: 1;
  transform: translateY(0);
}

/* Радиокнопки */
:deep(.el-radio) {
  display: flex;
  align-items: center;
  gap: 0.1rem;
  color: rgb(var(--text-secondary-rgb)); /* Базовый цвет */
  font-weight: 500;
}

:deep(.el-radio:hover) {
  color: color-mix(in srgb, rgb(var(--color-primary-rgb)) 30%, rgb(var(--text-secondary-rgb)) 70%);
  font-weight: 600;
}

:deep(.el-radio:hover .el-radio__label) {
  color: color-mix(in srgb, rgb(var(--color-primary-rgb)) 30%, rgb(var(--text-secondary-rgb)) 70%);
  font-weight: 600;
}

:deep(.el-radio.is-checked) {
  color: rgb(var(--color-primary)) !important;
  font-weight: 700;
}

:deep(.el-radio.is-checked .el-radio__label) {
  color: var(--color-primary) !important;
  font-weight: 700 !important;
}

:deep(.el-radio__label) {
  font-size: 1rem;
}

:deep(.el-radio.is-checked .el-radio__inner) {
  border-color: var(--color-primary);
  background-color: var(--color-primary);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  height: 0;
  opacity: 0;
}

.expand-enter-to,
.expand-leave-from {
  height: auto;
  opacity: 1;
}

</style>

