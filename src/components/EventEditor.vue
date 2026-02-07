<template>
  <el-form :model="form" label-position="top">
    <!-- Название -->
    <el-form-item label="Название события">
      <el-input
          v-model="form.name"
          :maxlength="100"
          show-word-limit
          clearable
      />
    </el-form-item>

    <!-- Комментарий -->
    <el-form-item label="Комментарий">
      <el-input
          type="textarea"
          v-model="form.description"
          rows="3"
          clearable
      />
    </el-form-item>

    <!-- Активность -->
    <el-form-item>
      <el-switch v-model="form.isActive" active-text="Активно" />
    </el-form-item>

    <!-- Режим события + Повторяемость -->
    <el-form-item>
      <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center;">
        <el-segmented
            v-model="eventMode"
            :options="[
            { label: 'По датам', value: 'dates' },
            { label: 'По месяцам', value: 'months' }
          ]"
            size="small"
        />
        <el-checkbox v-model="isRecurring" label="Повторяемое" />
      </div>
    </el-form-item>

    <!-- Режим по датам -->
    <template v-if="eventMode === 'dates'">
      <!-- start / end datetime всегда при dates, просто без RecurringBlock если !isRecurring -->
      <el-form-item label="Дата и время начала">
        <el-date-picker
            v-model="form.dateStart"
            type="datetime"
            placeholder="Дата и время начала"
            :disabled-date="date => date < new Date()"
            style="width: 100%;"
        />
      </el-form-item>

      <el-form-item label="Дата и время окончания">
        <el-date-picker
            v-model="form.dateEnd"
            type="datetime"
            placeholder="Дата и время окончания"
            :disabled-date="date => date < new Date()"
            style="width: 100%;"
        />
      </el-form-item>

      <!-- Recurring block: только при dates && isRecurring -->
      <RecurringBlock
          v-if="isRecurring"
          v-model="form.recurrence"
      />
    </template>

    <!-- Режим по месяцам -->
    <template v-else-if="eventMode === 'months'">
      <!-- Базовые поля месячного режима (всегда) -->
      <el-form-item label="Date mode" prop="date_mode">
        <el-select
            v-model="form.date_mode"
            placeholder="Select date mode"
        >
          <el-option label="Точная дата" value="exact_date" />
          <el-option label="номер месяца" value="number_of_month" />
          <el-option label="N-я неделя" value="number_of_week" />
        </el-select>
      </el-form-item>

      <el-form-item label="Год" prop="month_year">
        <el-input-number
            v-model="form.month_year"
            :min="0"
            :step="1"
            :controls="false"
            style="width: 100%;"
        />
      </el-form-item>

      <el-form-item label="Месяц" prop="month_number">
        <el-input-number
            v-model="form.month_number"
            :min="1"
            :max="12"
            :step="1"
            :controls="false"
            style="width: 100%;"
        />
      </el-form-item>

      <!-- Только при months && повтор -->
      <template v-if="isRecurring">
        <el-form-item label="Интервал (месяцев)" prop="month_interval">
          <el-input-number
              v-model="form.month_interval"
              :min="1"
              :step="1"
              :controls="false"
              style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="На сколько месяцев" prop="months_span">
          <el-input-number
              v-model="form.months_span"
              :min="1"
              :step="1"
              :controls="false"
              style="width: 100%;"
          />
        </el-form-item>
      </template>
    </template>

    <!-- Duration — всегда -->
    <el-form-item label="Длительность (минуты)" prop="duration_minutes">
      <el-input-number
          v-model="form.durationMinutes"
          :min="0"
          :step="5"
          :controls="false"
          style="width: 100%;"
      />
    </el-form-item>

    <!-- Финансовый блок -->
    <el-form-item>
      <el-checkbox v-model="isFinancial" label="Финансовое" />
    </el-form-item>

    <div>
      <FinancialBlock v-if="isFinancial" :form="form" />
    </div>

    <!-- Кнопка сохранить -->
    <el-form-item>
      <el-button
          type="primary"
          @click="submitForm"
          :loading="submitting"
      >
        Сохранить
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import FinancialBlock from './FinancialBlock.vue'
import RecurringBlock from './RecurringBlock.vue'
import { ElMessage, ElLoading } from 'element-plus'
import axios from '@/axios'

const emit = defineEmits(['complete'])

const props = defineProps({
  initialEvent: {
    type: Object,
    default: null
  }
})

const submitting = ref(false)
const isRecurring = ref(false)
const isFinancial = ref(false)

// 'dates' | 'months'
const eventMode = ref('dates')

const form = ref({
  name: '',
  description: '',
  isActive: true,

  // финансы
  currency: 'RUB',
  amountRub: null,
  foreignAmount: null,
  isFinancialEvent: false,
  account: null,

  // повторяемость
  recurrence: null,

  // режим по датам
  dateStart: '',
  dateEnd: '',

  // длительность
  durationMinutes: null,

  // режим по месяцам
  date_mode: 'exact_date',
  month_year: null,
  month_number: null,
  month_interval: 1,
  months_span: 1
})

// Заполнить форму при редактировании
onMounted(() => {
  if (props.initialEvent) {
    const event = props.initialEvent

    // определить режим по наличию date_mode
    eventMode.value = event.date_mode ? 'months' : 'dates'

    form.value = {
      name: event.name || '',
      description: event.description || '',
      isActive: event.is_active ?? true,

      currency: 'RUB',
      amountRub: event.amount ?? null,
      foreignAmount: null,
      isFinancialEvent: !!event.amount,
      account: event.account || null,

      recurrence: event.recurrence || null,

      dateStart: event.start_datetime
          ? new Date(event.start_datetime)
          : '',
      dateEnd: event.end_datetime
          ? new Date(event.end_datetime)
          : '',

      durationMinutes: event.duration_minutes ?? null,

      date_mode: event.date_mode || 'exact_date',
      month_year: event.month_year ?? null,
      month_number: event.month_number ?? null,
      month_interval: event.month_interval ?? 1,
      months_span: event.months_span ?? 1
    }

    isFinancial.value = !!event.amount

    if (eventMode.value === 'dates') {
      isRecurring.value = !!event.recurrence
    } else {
      isRecurring.value =
          !!event.month_interval ||
          (typeof event.months_span === 'number' && event.months_span > 1)
    }
  }
})

// Синхронизация чекбокса "Финансовое"
watch(isFinancial, (val) => {
  form.value.isFinancialEvent = val
  if (!val) {
    form.value.amountRub = null
  }
})

const submitForm = async () => {
  submitting.value = true
  const loading = ElLoading.service({ text: 'Сохраняем...', fullscreen: true })

  try {
    const isDatesMode = eventMode.value === 'dates'
    const isMonthsMode = eventMode.value === 'months'

    const payload = {
      name: form.value.name,
      description: form.value.description,
      is_active: form.value.isActive,

      // финансы
      account: form.value.isFinancialEvent ? form.value.account || null : null,
      amount: form.value.isFinancialEvent
          ? form.value.amountRub ?? '0.00'
          : null,

      // даты
      start_datetime:
          isDatesMode && form.value.dateStart
              ? new Date(form.value.dateStart).toISOString()
              : null,
      end_datetime:
          isDatesMode && form.value.dateEnd
              ? new Date(form.value.dateEnd).toISOString()
              : null,

      // длительность
      duration_minutes: form.value.durationMinutes ?? null,

      // повторяемость по датам
      recurrence:
          isDatesMode && isRecurring.value
              ? form.value.recurrence || null
              : null,

      // месячный режим
      date_mode: form.value.date_mode,
      month_year: isMonthsMode ? form.value.month_year : null,
      month_number: isMonthsMode ? form.value.month_number : null,
      month_interval:
          isMonthsMode && isRecurring.value
              ? form.value.month_interval
              : null,
      months_span:
          isMonthsMode && isRecurring.value
              ? form.value.months_span
              : null,

      // остальное как раньше
      status: props.initialEvent?.status || 'incomplete',
      is_task: props.initialEvent?.is_task ?? false,
      tags: props.initialEvent?.tags ?? []
    }

    const method = props.initialEvent ? 'PATCH' : 'POST'
    const url = props.initialEvent
        ? `schedule/events/${props.initialEvent.id}/`
        : 'schedule/events/'

    const result = await axios({
      method,
      url,
      headers: { 'Content-Type': 'application/json' },
      data: payload
    })

    ElMessage.success(
        props.initialEvent
            ? 'Событие обновлено 💫'
            : 'Событие создано! 🎉'
    )
    console.log('✅ Успешно:', result)
    emit('complete')
  } catch (err) {
    console.error(err)
    ElMessage.error('Не удалось сохранить событие 😢')
  } finally {
    submitting.value = false
    loading.close()
  }
}
</script>

<style scoped>
.input-field {
  margin-bottom: 1rem;
}
</style>
