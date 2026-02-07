<template>
  <el-form :model="form" label-position="top">
    <el-row>
      <el-col :span="12">
        <el-form-item label="Amount (₽)">
          <el-input
            v-model="form.amountRub"
            type="number"
            placeholder="₽"
            :min="0"
          />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Account">
          <el-select
            v-model="form.account"
            placeholder="Счёт"
            class="input-field"
            :loading="loading"
            clearable
          >
            <el-option
              v-for="account in accounts"
              :key="account.id"
              :label="`${account.name} (${account.amount}₽)`"
              :value="account.id"
            />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>
  </el-form>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import axios from '@/axios'

const props = defineProps({ form: Object })

const accounts = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await axios.get('accounting/accounts/')
    accounts.value = data
  } catch (err) {
    ElMessage.error('Не удалось загрузить аккаунты 😢')
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script>
