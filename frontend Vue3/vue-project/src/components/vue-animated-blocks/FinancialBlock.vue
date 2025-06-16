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
      </el-button>
    </div>

    <transition name="fade-slide">
      <div v-show="isActive">
        <!-- Сумма -->
        <label class="field-label">
          Велечина затрат:
          <el-tooltip content="Введите сколько пришло в рублях" placement="top">
            <span style="cursor: pointer;">&#9432;</span>
          </el-tooltip>
        </label>

        <!-- Поля в одной строке -->
        <div class="amount-row">
          <el-input v-model="form.amountRub" type="number" placeholder="₽" class="input-field" />
          <el-input v-model="form.foreignAmount" type="number" placeholder="$" class="input-field" />
        </div>

        <!-- Аккаунт -->
        <label class="field-label">С какого счета списываем:</label>
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

const props = defineProps({ form: Object })
const isActive = ref(false)

watch(isActive, (val) => {
  props.form.isFinancialEvent = val
})
</script>

<style scoped>
.financial-block {
  padding: 1rem;
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

.financial-title {
  font-size: 0.8rem;
  font-weight: 400;
  color: var(--text-secondary);
  color: color-mix(in srgb, var(--text-main) 70%, var(--bg-main) 30%);
  text-align: left;
  transition: all 0.3s ease;
}

.financial-title.active {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-main);
  text-align: center;
}

.switch {
  --el-switch-on-color: var(--color-primary);
  --el-switch-off-color: var(--text-secondary);
}

.field-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 0.3rem;
  user-select: none;
}

.amount-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.amount-row .input-field {
  flex: 0 0 120px;
}

.input-field {
  margin-bottom: 1rem;
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

:deep(.circle-checkbox .el-checkbox__inner) {
  border-radius: 50%;         /* превращаем квадрат в круг */
  width: 18px;                /* задаём размер */
  height: 18px;
}

:deep(.circle-checkbox .el-checkbox__inner::after) {
  top: 3px;                   /* регулируем “галочку” или внутренний кружок */
  left: 3px;
  width: 6px;
  height: 6px;
  border-radius: 50%;         /* делаем внутренний маркер круглым */
  background-color: var(--color-primary);
  transform: scale(1);
}

:deep(.circle-checkbox.is-checked .el-checkbox__inner) {
  border-color: var(--color-primary);
  background-color: transparent; /* убираем заливку, оставляем только внутренний кружок */
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

</style>
