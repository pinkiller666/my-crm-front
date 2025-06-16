<template>
  <div class="financial-block">
    <div :class="['financial-header', { active: isActive }]">
      <el-button
          :type="isActive ? 'primary' : ''"
          :text="!isActive"
          plain
          round
          @click="isActive = !isActive"
          :class="['financial-button', { active: isActive }]"
      >
        Есть затраты
        <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
      </el-button>
    </div>

    <transition name="fade-slide">
      <div v-show="isActive">
        <!-- Сумма -->
        <label class="field-label">

          Сколько:
          <el-tooltip content="Введите сколько пришло в рублях" placement="top">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </label>

        <!-- Поля в одной строке -->
        <div class="amount-row">
          <el-input v-model="form.amountRub" type="number" placeholder="₽" class="input-field" />
        </div>

        <!-- Аккаунт -->
        <label class="field-label">С какого счета:</label>
        <el-select v-model="form.account" placeholder="Выберите аккаунт" class="input-field">
          <el-option label="Единорог" value="unicorn" />
          <el-option label="Лягушка" value="frog" />
          <el-option label="Драконозавр" value="dragon" />
        </el-select>
      </div>
    </transition>
  </div>
</template>


<script setup>
import { ref, watch } from 'vue'
import { ArrowDown, InfoFilled } from '@element-plus/icons-vue'


const props = defineProps({ form: Object })
const isActive = ref(false)

watch(isActive, (val) => {
  props.form.isFinancialEvent = val
})
</script>

<style scoped>
.financial-block {
  padding: 1rem;
  --el-color-primary: var(--color-success);
}

.financial-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  justify-content: flex-start;
  transition: all 0.3s ease;
}

.financial-header.active {
  justify-content: center;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 0em;
  user-select: none;
}

.amount-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0rem;
}

.amount-row .input-field {
  flex: 0 0 120px;
}

.input-field {
  margin-bottom: 0.5rem;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-slide-enter-to,
.fade-slide-leave-from {
  opacity: 1;
  transform: translateY(0);
}

.financial-button {
  font-size: 0.9rem;
  font-weight: 400;
  color: color-mix(in srgb, var(--text-main) 40%, var(--bg-main) 60%) !important;
  border-color: transparent;
  transition: all 0.3s ease;
}

:deep(.financial-button:hover) {
  color: var(--color-primary) !important;
  background-color: color-mix(in srgb, var(--color-primary) 20%, var(--bg-main) 80%) !important;
}

:deep(.financial-button.active) {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-primary) !important;
  background-color: color-mix(in srgb, var(--color-primary) 20%, var(--bg-main) 80%) !important;
  border-color: transparent !important;
}

:deep(.financial-button.active:hover) {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-primary);
  background-color: color-mix(in srgb, var(--color-primary) 40%, var(--bg-main) 60%) !important;
  border-color: transparent !important;
}

.dropdown-icon {
  margin-left: 0.5rem;
  font-size: 1em;
  transition: transform 0.3s ease;
}

.financial-button.active .dropdown-icon {
  transform: rotate(180deg); /* переворачиваем при isActive */
}

</style>
