<template>
  <div>
    <el-radio-group v-model="currentMode">
      <el-radio-button v-for="(mode, index) in repeatModes" :key="index" :label="index">
        {{ mode.label }}
      </el-radio-button>
    </el-radio-group>

    <div v-if="currentMode === 0">
<div>Повторяется по дням недели:</div>
<el-checkbox-group v-model="selectedDays">
  <el-checkbox v-for="(day, code) in weekdayMap" :key="code" :label="day.code">
    {{ day.label }}
  </el-checkbox>
</el-checkbox-group>
    </div>


    <div v-else-if="currentMode === 1">
      <div>Повторяется по числам месяца:</div>
      <div v-for="(day, index) in repeatDays" :key="index">
        <el-input-number v-model="repeatDays[index]" :min="1" :max="31" class="block-number" />
      </div>
      <el-button type="primary" @click="addDay">Добавить число</el-button>
    </div>

    <div v-else-if="currentMode === 2">
      <div>Повторяется каждые N дней:</div>
      <el-input-number v-model="intervalDays" :min="1" />
    </div>

    <div style="margin-top: 1rem;">
      <div>Период действия:</div>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="—"
        start-placeholder="Начало"
        end-placeholder="Конец"
        format="DD.MM.YYYY"
      />
      <el-button type="primary" @click="setHalfYear">На полгода</el-button>
    </div>

    <div style="margin-top: 1rem;">
      <div>RRULE:</div>
      <el-input v-model="rruleString" readonly />
    </div>

    <div style="margin-top: 1rem;">
      <div>{{ humanReadable }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const emit = defineEmits(['update:modelValue'])

const props = defineProps({
  modelValue: String
})

const repeatModes = [
  { label: 'По дням недели' },
  { label: 'По числам месяца' },
  { label: 'Каждые N дней' }
]

const weekdayMap = {
  MO: { code: 'MO', label: 'Пн' },
  TU: { code: 'TU', label: 'Вт' },
  WE: { code: 'WE', label: 'Ср' },
  TH: { code: 'TH', label: 'Чт' },
  FR: { code: 'FR', label: 'Пт' },
  SA: { code: 'SA', label: 'Сб' },
  SU: { code: 'SU', label: 'Вс' }
}

const currentMode = ref(0)
const selectedDays = ref([]) // теперь храним коды ("MO", "TU" и т.д.)
const repeatDays = ref([1])
const intervalDays = ref(1)
const dateRange = ref([])
const rawModelValue = ref(props.modelValue || '')

const isParsing = ref(false) // 🔥 флаг чтобы избежать циклов

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
  let dateText = ''

  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value.map(date =>
      new Intl.DateTimeFormat('ru-RU').format(date)
    )
    dateText = ` с ${start} по ${end}`
  }

  switch (currentMode.value) {
    case 0:
      if (!selectedDays.value.length) return ''
      return `Каждую ${selectedDays.value.map(d => weekdayMap[d].label).join(', ')}${dateText}`

    case 1: {
      const days = repeatDays.value.filter(Boolean).join(', ')
      if (!days) return ''
      return `${days}-го числа каждого месяца${dateText}`
    }

    case 2:
      return `Каждые ${intervalDays.value} дней${dateText}`

    default:
      return ''
  }
})


const rruleString = computed(() => {
  let dtstart = ''
  let until = ''

  if (dateRange.value && dateRange.value.length === 2) {
    dtstart = dateRange.value[0].toISOString().split('T')[0].replace(/-/g, '')
    until = dateRange.value[1].toISOString().split('T')[0].replace(/-/g, '')
  }

  let rruleParts = []

  switch (currentMode.value) {
    case 0: {
      if (!selectedDays.value.length) return rawModelValue.value
      rruleParts.push(`FREQ=WEEKLY`)
      rruleParts.push(`BYDAY=${selectedDays.value.join(',')}`)
      break
    }
    case 1: {
      const days = repeatDays.value.filter(Boolean).join(',')
      if (!days) return rawModelValue.value
      rruleParts.push(`FREQ=MONTHLY`)
      rruleParts.push(`BYMONTHDAY=${days}`)
      break
    }
    case 2: {
      const interval = intervalDays.value || 1
      rruleParts.push(`FREQ=DAILY`)
      rruleParts.push(`INTERVAL=${interval}`)
      break
    }
    default:
      return rawModelValue.value
  }

  if (until) {
    rruleParts.push(`UNTIL=${until}`)
  }

  let rrule = `RRULE:${rruleParts.join(';')}`
  if (dtstart) {
    rrule = `DTSTART:${dtstart}\n${rrule}`
  }

  return rrule
})


// 📤 отправляем наружу
watch(rruleString, (val) => {
  if (!isParsing.value) {
    emit('update:modelValue', val)
  }
})

// 📥 парсим при изменении props
watch(() => props.modelValue, (val) => {
  if (val) {
    isParsing.value = true
    parseRRule(val)
    rawModelValue.value = val
    isParsing.value = false
  }
}, { immediate: true })

function parseRRule(rruleStr) {
  const lines = rruleStr.trim().split('\n')
  let dtstartRaw = ''
  let ruleRaw = ''

  for (const line of lines) {
    if (line.startsWith('DTSTART')) {
      dtstartRaw = line.replace('DTSTART:', '')
    } else if (line.startsWith('RRULE')) {
      ruleRaw = line.replace('RRULE:', '')
    }
  }

  const ruleParts = Object.fromEntries(
    ruleRaw.split(';').map(p => {
      const [key, val] = p.split('=')
      return [key, val]
    })
  )

  const dtstart = parseRRDate(dtstartRaw)
  const until = parseRRDate(ruleParts.UNTIL)
  if (dtstart && until) {
    dateRange.value = [dtstart, until]
  }

  const freq = ruleParts.FREQ
  switch (freq) {
    case 'WEEKLY':
      currentMode.value = 0
      selectedDays.value = (ruleParts.BYDAY || '').split(',').filter(Boolean)
      break
    case 'MONTHLY':
      currentMode.value = 1
      repeatDays.value = (ruleParts.BYMONTHDAY || '')
        .split(',')
        .map(d => parseInt(d))
        .filter(Boolean)
      break
    case 'DAILY':
      currentMode.value = 2
      intervalDays.value = parseInt(ruleParts.INTERVAL || '1')
      break
  }
}

function parseRRDate(yyyymmdd) {
  if (!yyyymmdd || yyyymmdd.length !== 8) return null
  const year = +yyyymmdd.slice(0, 4)
  const month = +yyyymmdd.slice(4, 6) - 1
  const day = +yyyymmdd.slice(6, 8)
  return new Date(Date.UTC(year, month, day))
}
</script>


<style scoped>
.block-number {
  margin: 0.5rem 0;
}
</style>
