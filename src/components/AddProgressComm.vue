<template>
  <div class="add-progress-container">
    <h3 class="form-title">Добавить заказ</h3>

    <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-position="top"
        class="form-block"
    >
      <el-form-item label="Выбери художника:" prop="artist">
        <el-select v-model="form.artist" placeholder="Выберите художника">
          <el-option
              v-for="artist in artistList"
              :key="artist.id"
              :label="artist.name"
              :value="artist.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="Сумма ($)" prop="amount">
        <el-input
            v-model="form.amount"
            placeholder="Сколько $"
            type="number"
        />
      </el-form-item>

      <el-form-item label="Комментарий:" prop="comment">
        <el-input
            v-model="form.comment"
            type="textarea"
            :rows="4"
            placeholder="Комментарий к заказу"
        />
      </el-form-item>

      <div class="button-wrap">
        <el-button type="primary" @click="submitForm">Сохранить</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const form = ref({
  artist: null,
  amount: null,
  comment: ''
})

const formRef = ref()

defineProps({
  artistList: Array
})

// 💡 Валидация
const rules = {
  artist: [
    { required: true, message: 'Выберите художника', trigger: 'blur' }
  ],
  amount: [
    { required: true, message: 'Введите сумму', trigger: 'blur' },
    {
      type: 'number',
      message: 'Сумма должна быть числом от 1 до 99999',
      transform: value => Number(value),
      validator: (_, value) =>
          Number.isInteger(value) && value >= 1 && value <= 99999
    }
  ],
  comment: [
    {
      validator: (_, value) => !value || value.length <= 500,
      message: 'Комментарий слишком длинный (макс. 500 символов)',
      trigger: 'blur'
    }
  ]
}

// 🎯 Сабмит
async function submitForm() {

  console.log('[DEBUG] Сохраняем данные:', form.value)

  formRef.value.validate(async valid => {
    if (!valid) return ElMessage.error('Форма невалидна')

    try {
      const response = await fetch('/api/progress/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(form.value),
      })

      if (!response.ok) throw new Error('Сервер вернул ошибку')

      const data = await response.json()

      ElMessage.success(`Комиссия успешно создана!`)
      form.value = { artist: null, amount: null, comment: '' }
    } catch (err) {
      console.error(err)
      ElMessage.error('Ошибка при отправке на сервер')
    }
  })
}



</script>

<style scoped>
.add-progress-container {
  width: 100%;
  padding: 2rem;
  background-color: var(--bg-secondary);
  border-radius: var(--radius-card);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  max-width: 640px;
}

.form-block {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-title {
  text-align: center;
  margin-bottom: 1rem;
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--text-main);
}

/* 🧁 Все поля и выпадашки — общая логика */
:deep(.el-input__wrapper),
:deep(.el-textarea__inner),
:deep(.el-select .el-input__wrapper) {
  background-color: var(--bg-main) !important;
  color: var(--text-main) !important;
  border-radius: var(--radius-card);
  border: 1px solid var(--border-color);
  transition: box-shadow 0.2s ease;
}

/* 🎯 При фокусе — светится */
:deep(.el-input__wrapper.is-focus),
:deep(.el-textarea__inner:focus),
:deep(.el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--color-primary);
  background-color: var(--bg-main) !important;
}

:deep(.el-input__inner) {
  background-color: var(--bg-main) !important;
}

/* 🔘 Выпадающее меню */
:deep(.el-select-dropdown) {
  background-color: var(--bg-main) !important;
  color: var(--bg-main) !important;
  border-radius: var(--radius-card) !important;
}

/* 🧷 Обводка по умолчанию (если нужна тонкая) */
:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  border: 1px solid var(--border-color);
}

/* 🧷 Тонкая тень/hover если хочешь добавить интерактив */
:deep(.el-input__wrapper:hover),
:deep(.el-select .el-input__wrapper:hover),
:deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 2px var(--color-primary-light-3);
}

:deep(input[type="number"]::-webkit-outer-spin-button),
:deep(input[type="number"]::-webkit-inner-spin-button) {
  -webkit-appearance: none;
  margin: 0;
}

/* Кнопка */
.button-wrap {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

:deep(.el-select .el-input__wrapper) {
  background-color: var(--bg-main) !important;
}

:deep(.el-select__wrapper) {
  background-color: var(--bg-main) !important;
}

</style>
