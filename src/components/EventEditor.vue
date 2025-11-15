<template>

      <el-form :model="form" label-position="top">

        <el-form-item label="Название события">
          <el-input
            v-model="form.name"
            :maxlength="100"
            show-word-limit
            clearable
          />
        </el-form-item>

        <el-form-item label="Комментарий">
          <el-input
            type="textarea"
            v-model="form.description"
            rows="3"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-switch
            v-model="form.isActive"
            active-text="Активно"
          />
        </el-form-item>

        <el-form-item>
          <el-date-picker
            v-model="form.date"
            type="datetime"
            placeholder="Дата события"
            :disabled-date="date => date < new Date()"
          />
        </el-form-item>

          <el-checkbox v-model="isRecurring" label="Повторяемое" />
          <div>
          <RecurringBlock v-if="isRecurring" v-model="form.recurrence" />
          </div>


          <el-checkbox v-model="isFinancial" label="Финансовое" />
          <div>
          <FinancialBlock v-if="isFinancial" :form="form" />
          </div>

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

// Props
const props = defineProps({
  initialEvent: {
    type: Object,
    default: null
  }
})

const submitting = ref(false)
const isRecurring = ref(false)
const isFinancial = ref(false)

const form = ref({
  name: '',
  description: '',
  isActive: true,
  currency: 'RUB',
  amountRub: null,
  recurrence: null,
  foreignAmount: null,
  date: '',
  dateStart: '',
  dateEnd: '',
  isFinancialEvent: false,
  account: null
})

// Заполнить форму если передан initialEvent
onMounted(() => {
  if (props.initialEvent) {
    const event = props.initialEvent
    form.value = {
      name: event.name || '',
      description: event.description || '',
      isActive: event.is_active ?? true,
      currency: 'RUB',
      amountRub: event.amount ?? null,
      foreignAmount: null,
      date: event.start_datetime
        ? new Date(event.start_datetime)
        : '',
      dateStart: '',
      dateEnd: '',
      isFinancialEvent: !!event.amount,
      account: event.account || null,
      recurrence: event.recurrence || null
    }

    isFinancial.value = !!event.amount
    isRecurring.value = !!event.recurrence
  }
})

// Watch чекбокса "Финансовое"
watch(isFinancial, (val) => {
  form.value.isFinancialEvent = val
})

const submitForm = async () => {
  submitting.value = true
  const loading = ElLoading.service({ text: 'Сохраняем...', fullscreen: true })

  const payload = {
    name: form.value.name,
    description: form.value.description,
    is_active: form.value.isActive,
    account: form.value.account || null,
    amount: form.value.amountRub ?? '0.00',
    recurrence: form.value.recurrence || null,
    start_datetime: form.value.date
      ? new Date(form.value.date).toISOString()
      : null,
    end_datetime: null,
    duration_minutes: null,
    status: 'incomplete',
    is_task: false,
    tags: []
  }

  try {
    const method = props.initialEvent ? 'PATCH' : 'POST';
    const url = props.initialEvent
        ? `schedule/events/${props.initialEvent.id}/`
        : 'schedule/events/';

    const result = await axios({
      method: method,
      url: url,
      headers: { 'Content-Type': 'application/json' },
      data: payload
    });

    ElMessage.success(props.initialEvent
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

