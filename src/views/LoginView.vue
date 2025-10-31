<template>
  <div>
    <el-card>
      <h2>Login</h2>

      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <!-- Username -->
        <el-form-item label="Username" prop="username">
          <el-input
            v-model="form.username"
            placeholder="Enter your username"
            clearable
          />
        </el-form-item>

        <!-- Password -->
        <el-form-item label="Password" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="Enter your password"
            show-password
          />
        </el-form-item>

  <!-- Error feedback -->
  <el-alert
    v-if="error"
    title="Error"
    :description="error"
    type="error"
    show-icon
    :closable="false"
  />

        <!-- Submit button -->
        <el-form-item>
          <el-button
            type="primary"
            class="w-full"
            :loading="loading"
            @click="onSubmit"
          >
            Login
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import { ElMessage } from "element-plus"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()

const formRef = ref(null)
const form = reactive({
  username: "",
  password: "",
})

const error = ref(null)
const loading = ref(false)

const rules = {
  username: [{ required: true, message: "Username is required", trigger: "blur" }],
  password: [{ required: true, message: "Password is required", trigger: "blur" }],
}

const onSubmit = async () => {
  error.value = null
  loading.value = true

  try {
    await formRef.value.validate()

    await auth.login(form.username, form.password)

    ElMessage.success("Login successful 🎉")
    // редиректим на главную или дашборд
    window.location.href = "/"
  } catch (err) {
    if (err.response && err.response.status === 401) {
      error.value = "Invalid username or password"
    } else if (err.response) {
      error.value = "Something went wrong, try again"
    } else {
      error.value = "Unexpected error"
    }
  } finally {
    loading.value = false
  }
}
</script>
