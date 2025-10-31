<template>
  <div class="navbar-container" v-if="auth.isAuthenticated">
    <!-- Меню навигации -->
    <el-menu
      :default-active="activeMenu"
      class="navbar"
      mode="horizontal"
      @select="handleSelect"
    >
      <el-menu-item
        v-for="tab in tabs"
        :key="tab.path"
        :index="tab.path"
      >
        {{ tab.label }}
      </el-menu-item>
    </el-menu>

    <!-- Пользовательская зона -->
    <div class="user-info" >
      <span>{{ auth.user?.name || auth.user?.username }}</span>
      <el-button type="primary" size="small" @click="auth.logout">Logout</el-button>

    <ThemeSwitcher />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ThemeSwitcher from '@/components/ThemeSwitcher.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

// вкладки
const tabs = [
  { label: 'Timeline', path: '/' },
  { label: 'Финансы', path: '/finance' },
  { label: 'На день', path: '/daily' }
]

// текущее активное меню
const activeMenu = ref(route.path)
watch(() => route.path, (newPath) => {
  activeMenu.value = newPath
})

// переход по клику
function handleSelect(path) {
  if (path !== route.path) {
    router.push(path)
  }
}
</script>

<style scoped>
.navbar-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar {
  flex-grow: 1;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
