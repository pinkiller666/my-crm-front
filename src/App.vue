<template>
    <NavBar />
  <div class="app">
    <div class="container">
      <div class="content-wrapper">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
</script>

<style scoped>
/* Основной контейнер приложения */
.app {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

/* Контейнер контента */
.container {
  width: 100%;
  flex-grow: 1;
  display: flex;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
}

/* Обертка контента */
.content-wrapper {
  max-width: 1200px;
  width: 100%;
  box-sizing: border-box;
  padding: 20px;
  border-radius: 10px;
  margin: 0 auto;
}
</style>
