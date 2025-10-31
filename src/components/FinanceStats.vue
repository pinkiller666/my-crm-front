<template>
  <div v-loading="loading" element-loading-text="Загрузка бюджета...">
    <el-row :gutter="16" v-if="budget">
      <!-- Текущий баланс -->
      <el-col :xs="24" :sm="12" :md="8" class="mb-4">
        <div class="statistic-card">
          <el-statistic :value="budget.remaining_rub" title="Текущий баланс">
            <template #formatter="{ value }">
              <AmountNumber :amount="value" />
            </template>
          </el-statistic>
        </div>
      </el-col>

      <!-- Общий доход -->
      <el-col :xs="24" :sm="12" :md="8" class="mb-4">
        <div class="statistic-card">
          <el-statistic :value="budget.total_income_rub" title="Доход">
            <template #formatter="{ value }">
              <AmountNumber :amount="value" />
            </template>
          </el-statistic>
        </div>
      </el-col>

      <!-- Общие траты -->
      <el-col :xs="24" :sm="12" :md="8" class="mb-4">
        <div class="statistic-card">
          <el-statistic :value="budget.total_withdraw_rub" title="Расходы">
            <template #formatter="{ value }">
              <AmountNumber :amount="value" />
            </template>
          </el-statistic>
        </div>
      </el-col>

      <!-- Планируемые траты -->
      <el-col :xs="24" :sm="12" :md="8" class="mb-4">
        <div class="statistic-card">
          <el-statistic :value="budget.planned?.spend || 0" title="Планируемые траты">
            <template #formatter="{ value }">
              <AmountNumber :amount="value" />
            </template>
          </el-statistic>
        </div>
      </el-col>

      <!-- Планируемый доход -->
      <el-col :xs="24" :sm="12" :md="8" class="mb-4">
        <div class="statistic-card">
          <el-statistic :value="budget.planned?.earn || 0" title="Планируемый доход">
            <template #formatter="{ value }">
              <AmountNumber :amount="value" />
            </template>
          </el-statistic>
        </div>
      </el-col>

      <!-- Курсы валют -->
      <el-col :xs="24" :sm="12" :md="8" class="mb-4">
        <div class="statistic-card">
          <h4>Курсы валют</h4>
          <ul>
            <li v-for="(rate, currency) in budget.rates" :key="currency">
              {{ currency.toUpperCase() }}: {{ rate }}
            </li>
          </ul>
        </div>
      </el-col>
    </el-row>

    <el-empty v-else description="Нет данных за выбранный месяц" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import axios from "@/axios";
import AmountNumber from '@/components/AmountNumber.vue';

const props = defineProps({
  selectedMonthYear: {
    type: String,
    required: true
  }
});

const budget = ref(null);
const loading = ref(false);

async function fetchBudget() {
  loading.value = true;
  const [year, month] = props.selectedMonthYear.split('-').map(Number);
  try {
    const res = await axios.get(`accounting/budget/`, {
      params: { year, month }
    });
    budget.value = res.data;
  } catch (e) {
    console.error('Ошибка при получении бюджета:', e);
    budget.value = null;
  } finally {
    loading.value = false;
  }
}

// Следим за изменением props.selectedMonthYear
watch(() => props.selectedMonthYear, () => {
  fetchBudget();
}, { immediate: true });
</script>

<style scoped>
.statistic-card {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
</style>
