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
        Есть затраты
        <el-icon class="block-header-dropdown-icon"><ArrowDown /></el-icon>
      </el-button>
    </div>

    <transition name="fade-slide">
      <div v-show="isActive">
        <!-- Сумма -->
        <label class="block-field-label-v1">

          Сколько:
          <el-tooltip content="Введите сколько пришло в рублях" placement="top">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </label>

        <!-- Поля в одной строке -->
        <div class="amount-row">
          <el-input v-model="form.amountRub" type="number" placeholder="₽" class="block-input-field-v1" />
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
@import "@/assets/styles/BlockCard.css";
</style>
