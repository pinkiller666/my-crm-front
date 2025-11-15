<script setup>
import { computed } from 'vue'
import { useDevFlags } from '@/composables/useDevFlags'

const { devFlags, setUseNewCards } = useDevFlags()

const useNewCardsModel = computed({
  get() {
    return devFlags.useNewCards
  },
  set(value) {
    setUseNewCards(value)
  },
})
</script>

<template>
  <div class="dev-menu">
    <div class="dev-menu-header">
      <span class="dev-menu-dot">🛠</span>
      <span class="dev-menu-title">Dev panel</span>
    </div>

    <div class="dev-menu-row">
      <span class="dev-menu-label">TestVisual</span>

      <el-switch
          v-model="useNewCardsModel"
          size="small"
      />
    </div>
  </div>
</template>

<style scoped>
.dev-menu {
  position: fixed;
  top: 150px;
  left: 0px;

  z-index: 9999;

  padding: 8px 12px;
  border-radius: 10px;

  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(6px);

  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.12);

  font-size: 12px;
  line-height: 1.4;
  color: var(--el-text-color-regular);

  opacity: 0.5;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.dev-menu:hover {
  opacity: 1;
  transform: translateY(1px);
}

.dev-menu-header {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.dev-menu-dot {
  margin-right: 4px;
}

.dev-menu-title {
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-size: 11px;
}

.dev-menu-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: 2px;
}

.dev-menu-label {
  white-space: nowrap;
}
</style>
