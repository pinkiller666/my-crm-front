<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Grid as IconGrid } from '@element-plus/icons-vue'

type ThemeName = 'wood' | 'classic' | 'dark' | 'bubble-gum' | 'earth'

const savedTheme = localStorage.getItem('theme') as ThemeName | null
const theme = ref<ThemeName>(savedTheme || 'classic')

function switchTheme(val: string) {
  theme.value = val as ThemeName
  applyTheme()
  localStorage.setItem('theme', val)
}

function applyTheme() {
  document.documentElement.setAttribute('data-theme', theme.value)
  document.body.setAttribute('data-theme', theme.value)
  document.documentElement.setAttribute('data-theme', theme.value)

  const styleSource = getComputedStyle(document.documentElement)

  const varsToUpdate = [
    '--color-success',
    '--el-color-primary',
    '--el-color-primary-light-3',
    '--el-color-success',
    '--el-color-warning',
    '--el-color-error',
    '--el-color-info',
  ]

  for (const name of varsToUpdate) {
    const value = styleSource.getPropertyValue(name).trim()
    document.documentElement.style.setProperty(name, value)
  }

  localStorage.setItem('theme', theme.value)
}


onMounted(() => {
  applyTheme()
  document.documentElement.setAttribute('data-theme', theme.value)
})

watch(theme, () => {
  applyTheme()
})
</script>

<template>
  <!-- Кнопка тем в правом верхнем углу -->
  <el-dropdown trigger="click" @command="switchTheme">
    <el-button
        circle
        plain
        class="burger"
        :icon="IconGrid"
    />
    <!-- Меню выбора темы -->
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="classic">Classic</el-dropdown-item>
        <el-dropdown-item command="wood">Wood</el-dropdown-item>
        <el-dropdown-item command="earth">Earth</el-dropdown-item>
        <el-dropdown-item command="dark">Dark</el-dropdown-item>
        <el-dropdown-item command="bubble-gum">Bubble‑gum</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>
