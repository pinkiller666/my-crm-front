<template>
  <div class="auth-wrapper">
    <el-card class="auth-card">
      <h2>Регистрация</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="Имя" prop="name">
          <el-input v-model="form.name" placeholder="Отображаемое имя" clearable />
        </el-form-item>

        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" placeholder="name@example.com" clearable />
        </el-form-item>

        <el-form-item label="Логин" prop="username">
          <el-input v-model="form.username" placeholder="Выберите логин" clearable />
        </el-form-item>

        <el-form-item label="Пароль" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="Минимум 8 символов" />
        </el-form-item>

        <el-form-item label="Повторите пароль" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" show-password placeholder="Повторите пароль" />
        </el-form-item>

        <el-alert
          v-if="error"
          class="mb-3"
          type="error"
          :closable="false"
          :description="error"
          title="Ошибка"
          show-icon
        />

        <el-form-item>
          <el-button type="primary" class="w-full" :loading="loading" @click="onSubmit">
            Создать аккаунт
          </el-button>
        </el-form-item>

        <el-form-item>
          <el-button type="text" class="w-full" @click="goLogin">Уже есть аккаунт? Войти</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const formRef = ref()
const loading = ref(false)
const error = ref(null)

const form = reactive({
  name: '',
  email: '',
  username: '',
  password: '',
  confirmPassword: '',
})

const rules = {
  name: [
    { required: true, message: 'Введите имя, чтобы коллеги вас узнавали', trigger: 'blur' },
  ],
  email: [
    { required: true, message: 'Email обязателен', trigger: 'blur' },
    { type: 'email', message: 'Введите корректный email', trigger: ['blur', 'change'] },
  ],
  username: [
    { required: true, message: 'Введите логин', trigger: 'blur' },
    { min: 3, message: 'Минимум 3 символа', trigger: 'blur' },
  ],
  password: [
    { required: true, message: 'Введите пароль', trigger: 'blur' },
    { min: 8, message: 'Минимум 8 символов', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: 'Повторите пароль', trigger: 'blur' },
    {
      validator: (_, value, callback) => {
        if (!value) return callback(new Error('Повторите пароль'))
        if (value !== form.password) return callback(new Error('Пароли не совпадают'))
        return callback()
      },
      trigger: ['blur', 'change'],
    },
  ],
}

function formatErrorMessage(data) {
  if (!data) return 'Не удалось создать аккаунт'
  if (typeof data === 'string') return data
  if (Array.isArray(data)) return data.join('\n')
  if (typeof data === 'object') {
    return Object.values(data)
      .flat()
      .map((item) => (typeof item === 'string' ? item : JSON.stringify(item)))
      .join('\n')
  }
  return 'Не удалось создать аккаунт'
}

const onSubmit = async () => {
  error.value = null
  loading.value = true
  try {
    await formRef.value.validate()

    await auth.register({
      name: form.name,
      email: form.email,
      username: form.username,
      password: form.password,
    })

    ElMessage.success('Добро пожаловать! 🎉')
    router.push({ name: 'home' })
  } catch (err) {
    if (err?.response?.data) {
      error.value = formatErrorMessage(err.response.data)
    } else if (err instanceof Error && err.message) {
      error.value = err.message
    } else if (err && err !== false) {
      error.value = 'Что-то пошло не так'
    }
  } finally {
    loading.value = false
  }
}

const goLogin = () => {
  router.push({ name: 'login' })
}
</script>

<style scoped>
.auth-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.auth-card {
  max-width: 480px;
  width: 100%;
}

.w-full {
  width: 100%;
}

.mb-3 {
  margin-bottom: 1.5rem;
}
</style>
