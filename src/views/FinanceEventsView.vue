<template>
  <div>

<FinanceStats :selectedMonthYear="selectedMonthYear" />

    <el-row :gutter="20" class="mb-4">
      <el-col :span="8">
        <el-date-picker
          v-model="selectedMonthYear"
          type="month"
          placeholder="Выберите месяц"
          format="YYYY-MM"
          value-format="YYYY-MM"
        />
      </el-col>

      <el-col :span="8">
        <el-select v-model="selectedAccount" placeholder="Выберите аккаунт">
          <el-option
            v-for="acc in accounts"
            :key="acc.id"
            :label="acc.name"
            :value="acc.id"
          />
        </el-select>
      </el-col>

      <el-col :span="8">
        <el-button type="primary" @click="openCorrectionModal">Добавить корректировку</el-button>
      </el-col>
    </el-row>

    <div v-if="filteredEvents.length">
      <el-table :data="filteredEvents" style="width: 100%">
        <el-table-column prop="event.name" label="Название" />
        <el-table-column prop="event.description" label="Описание" />
        <el-table-column label="Сумма">
          <template #default="scope">
            <AmountNumber :amount="scope.row.event.amount" />
          </template>
        </el-table-column>
        <el-table-column prop="event.start_datetime" label="Начало" />
        <el-table-column prop="event.status" label="Статус" />
      </el-table>
    </div>

    <div v-else>
      <el-empty description="Нет событий за выбранный период" />
    </div>

    <!-- Модальное окно корректировки -->
    <el-dialog title="Добавить корректировочное событие" v-model="correctionModalVisible">
      <el-form :model="correctionForm" label-width="120px">
        <el-form-item label="Название">
          <el-input v-model="correctionForm.name" />
        </el-form-item>

        <el-form-item label="Сумма">
          <el-input v-model.number="correctionForm.amount" type="number" />
        </el-form-item>

        <el-form-item label="Дата">
          <el-date-picker v-model="correctionForm.start_datetime" type="date" placeholder="Выберите дату" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="correctionModalVisible = false">Отмена</el-button>
        <el-button type="primary" @click="submitCorrection">Добавить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from "vue"
import { ElMessage } from "element-plus"
import axios from "@/axios"
import AmountNumber from "@/components/AmountNumber.vue"
import FinanceStats from "@/components/FinanceStats.vue"

const accounts = ref([])
const events = ref([])

const selectedMonthYear = ref(`${new Date().getFullYear()}-${(new Date().getMonth() + 1).toString().padStart(2, '0')}`)
const selectedAccount = ref(null)

async function fetchAccounts() {
  try {
    const res = await axios.get("accounting/accounts/")
    accounts.value = res.data
    if (!selectedAccount.value && accounts.value.length) {
      selectedAccount.value = accounts.value[0].id
    }
  } catch (err) {
    console.error("Не удалось загрузить список аккаунтов", err)
    ElMessage.error("Не удалось загрузить аккаунты")
  }
}

async function fetchEvents() {
  const [year, month] = selectedMonthYear.value.split('-').map(Number)
  try {
    const res = await axios.get("schedule/all_events/", { params: { year, month } })
    events.value = res.data
  } catch (err) {
    console.error("Не удалось загрузить события", err)
    ElMessage.error("Не удалось загрузить события")
    events.value = []
  }
}

watch(selectedMonthYear, () => {
  fetchEvents()
}, { immediate: true })

const filteredEvents = computed(() => {
  if (!selectedAccount.value) return []
  return events.value.filter((e) => e.event.account === selectedAccount.value)
})

onMounted(async () => {
  await fetchAccounts()
})

// --- Модальное окно корректировки ---
const correctionModalVisible = ref(false)
const correctionForm = ref({
  name: "",
  amount: 0,
  start_datetime: "",
})

function openCorrectionModal() {
  if (!selectedAccount.value) {
    ElMessage.warning("Сначала выберите аккаунт")
    return
  }
  correctionForm.value = {
    name: "",
    amount: 0,
    start_datetime: "",
  }
  correctionModalVisible.value = true
}

async function submitCorrection() {
  if (!correctionForm.value.name || !correctionForm.value.amount || !correctionForm.value.start_datetime) {
    ElMessage.warning("Заполните все поля")
    return
  }

  const payload = {
    name: correctionForm.value.name,
    amount: correctionForm.value.amount,
    start_datetime: correctionForm.value.start_datetime,
    account: selectedAccount.value,
    is_balance_correction: true,
    status: "complete",
  }

  try {
    await axios.post("schedule/events/", payload)
    correctionModalVisible.value = false
    ElMessage.success("Корректировка добавлена")
    await fetchEvents()
  } catch (err) {
    console.error(err)
    ElMessage.error("Ошибка при добавлении корректировки")
  }
}
</script>

<style scoped>
.mb-4{
  margin-bottom: 4em;
}
</style>
