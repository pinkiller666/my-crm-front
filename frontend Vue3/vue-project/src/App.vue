<template>
  <div class="app">
    <NavBar />
    <ThemeSwitcher />
    <div class="container">
      <div class="content-wrapper">
        <router-view />
      </div>

      <!-- правая боковая панель -->
    </div>
  </div>
</template>

<script setup>
import NavBar    from '@/components/NavBar.vue'
import ThemeSwitcher from '@/components/ThemeSwitcher.vue'
</script>

<style scoped>
.container {
  display: flex;
  min-height: calc(100vh - 56px);    /* 56 px — высота NavBar */
}

.content-wrapper {
  flex: 1;
  overflow: auto;                    /* скроллим только контент */
}
</style>
