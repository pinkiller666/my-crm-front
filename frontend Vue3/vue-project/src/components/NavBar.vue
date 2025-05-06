<template>
  <!-- Навигация по разделам -->
  <el-tabs
      v-model="activeTab"
      type="card"
      class="navbar"
      @tab-click="handleClick"
  >
    <el-tab-pane
        v-for="tab in tabs"
        :key="tab.path"
        :label="tab.label"
        :name="tab.path"
    />
  </el-tabs>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

interface Tab { label: string; path: string }

// список вкладок — редактируйте здесь
const tabs: Tab[] = [
  { label: 'Главная',           path: '/' },
  { label: 'Добавить событие',  path: '/add-event' },
  { label: 'О нас',             path: '/about' },
  { label: 'Месячный прогресс', path: '/progress' }
]

const route = useRoute()
const router = useRouter()
const activeTab = ref<string>(route.path)
watch(() => route.path, p => (activeTab.value = p))

function handleClick(pane: any)
{
  const path = pane.props.name as string
  if (path !== route.path) router.push(path)
  const el = pane.$el as HTMLElement
  if (el) {
    el.classList.add('clicked')
    el.addEventListener('animationend', () => el.classList.remove('clicked'), { once: true })
  }
}
</script>

<style scoped>
/* Навбар: фон, паддинги и базовый размер текста */
.navbar {
  background: var(--bg-secondary);
  padding: 8px 16px;
  /* здесь устанавливайте желаемый размер текста вкладок */
  --tab-font-size: 28px;
  border-radius: 0 0 var(--radius-card) var(--radius-card);
}

/* Сброс фонового цвета и бордеров карточного контейнера */
:deep(.navbar.el-tabs--card,
       .navbar.el-tabs--card > .el-tabs__content) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

/* Стили вкладок */
:deep(.navbar .el-tabs__item) {
  font-weight: 500;
  color: var(--text-main) !important;
  padding: 10px 15px;
  background: transparent;
  cursor: pointer;
  transition: color .25s ease, background .2s ease;
}

/* Hover */
:deep(.navbar .el-tabs__item:hover) {
  color: var(--color-primary-hover) !important;
}
:deep(.el-tabs__item) {
  font-size: 18px !important;
  color: var(--text-main) !important;
}

/* Активная вкладка */
:deep(.navbar .el-tabs__item.is-active) {
  color: var(--el-color-primary) !important;
}

/* Анимация клика */
:deep(.navbar .el-tabs__item.clicked) {
  animation: clickPulse .3s ease;
  background: var(--color-primary-hover) !important;
}

:deep(.el-tabs__item:hover) {
  color: var(--color-primary-hover) !important;
}

:deep(.el-tabs__item.is-active) {
  color: var(--color-primary) !important;
}

@keyframes clickPulse {
  0%   { transform: scale(1); }
  50%  { transform: scale(.95); }
  100% { transform: scale(1); }
}
</style>
