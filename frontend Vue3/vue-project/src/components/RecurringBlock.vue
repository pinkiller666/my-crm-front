<template>
  <div class="block-v1">
    <div :class="['block-header-v1', { active: isActive }]">
      <el-button
          :type="isActive ? 'primary' : ''"
          :text="!isActive"
          plain
          round
          @click="isActive = !isActive"
          :class="['block-header-adjustments-v1', { active: isActive }]"
      >
        Как повторяется:
        <el-icon class="block-header-dropdown-icon"><ArrowDown /></el-icon>
      </el-button>
    </div>

    <transition name="block-fade-slide">
      <div v-if="isActive">
        <!-- 🔁 Переключатель режимов -->
        <div class="block-amount-row-v1" style="align-items: center; margin-top: 1rem;">
          <el-button @click="prevMode" :icon="ArrowLeft" circle />
          <div class="block-field-label-v1" style="flex: 1; justify-content: center;">
            {{ repeatModes[currentMode].label }}
          </div>
          <el-button @click="nextMode" :icon="ArrowRight" circle />
        </div>

        <!-- 🎯 Динамически отображаемые блоки -->
        <div v-if="currentMode === 0" class="block-input-field-v1">
          <div class="block-field-label-v1">Повторяется по дням недели:</div>
          <el-checkbox-group v-model="selectedDays">
            <el-checkbox label="Пн" />
            <el-checkbox label="Вт" />
            <el-checkbox label="Ср" />
            <el-checkbox label="Чт" />
            <el-checkbox label="Пт" />
            <el-checkbox label="Сб" />
            <el-checkbox label="Вс" />
          </el-checkbox-group>
        </div>

        <div v-else-if="currentMode === 1" class="block-input-field-v1">
          <div class="block-field-label-v1">Повторяется по числам месяца:</div>
          <div
              class="block-amount-row-v1"
              v-for="(day, index) in repeatDays"
              :key="index"
          >
            <el-input-number
                v-model="repeatDays[index]"
                :min="1"
                :max="31"
                class="block-number"
            />
          </div>
          <el-button type="primary" class="block-button-common" @click="addDay">
            Добавить число
          </el-button>
        </div>

        <div v-else-if="currentMode === 2" class="block-input-field-v1">
          <div class="block-field-label-v1">Повторяется каждые N дней:</div>
          <el-input-number v-model="intervalDays" :min="-3" />
        </div>

        <!-- 🗓️ Диапазон времени -->
        <div class="block-input-field-v1" style="margin-top: 1rem;">
          <div class="block-field-label-v1">Период действия:</div>
          <div class="block-amount-row-v1" style="flex-wrap: wrap;">
            <el-date-picker
                v-model="dateRange"
                type="daterange"
                unlink-panels
                range-separator="—"
                start-placeholder="Начало"
                end-placeholder="Конец"
                format="DD.MM.YYYY"
            />
            <el-button
                type="primary"
                class="block-button-common"
                @click="setHalfYear"
            >
              На полгода
            </el-button>
          </div>
        </div>

        <!-- Подставляем "человеко-подобное" описание -->
        <div class="block-input-field-v1" style="margin-top: 1rem;">
          <div class="block-field-label-v1">Описание повторения:</div>
          <div class="block-description-text">{{ humanReadable }}</div>
        </div>

      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ArrowDown, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { computed } from 'vue'


const isActive = ref(true)

const repeatModes = [
  { label: 'По дням недели' },
  { label: 'По числам месяца' },
  { label: 'Каждые N дней' }
]
const currentMode = ref(0)

const selectedDays = ref([])
const repeatDays = ref([1])
const intervalDays = ref(1)

const dateRange = ref([])

function prevMode() {
  currentMode.value = (currentMode.value + repeatModes.length - 1) % repeatModes.length
}

function nextMode() {
  currentMode.value = (currentMode.value + 1) % repeatModes.length
}

function addDay() {
  repeatDays.value.push(1)
}

function setHalfYear() {
  const start = new Date()
  const end = new Date()
  end.setMonth(start.getMonth() + 6)
  dateRange.value = [start, end]
}

const humanReadable = computed(() => {
  if (!dateRange.value || dateRange.value.length !== 2) return ''

  const [start, end] = dateRange.value.map(date =>
      new Intl.DateTimeFormat('ru-RU').format(date)
  )

  if (currentMode.value === 0) {
    if (selectedDays.value.length === 0) return ''
    return `Каждую ${selectedDays.value.join(', ')} с ${start} по ${end}`
  }

  if (currentMode.value === 1) {
    const days = repeatDays.value.filter(Boolean).join(', ')
    return `${days}-го числа каждого месяца с ${start} по ${end}`
  }

  if (currentMode.value === 2) {
    return `Каждые ${intervalDays.value} дней с ${start} по ${end}`
  }

  return ''
})

</script>

<style scoped>
@import "@/assets/styles/BlockCard.css";
</style>
