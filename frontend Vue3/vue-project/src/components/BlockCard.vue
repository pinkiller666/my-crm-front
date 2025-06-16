<template>
  <!-- Reusable styled card block -->
  <div class="block-v1">
    <!-- Header with title & optional toggle button -->
    <div class="block-header-v1" :class="{ centered: centerTitle }">
      <span class="block-title">
        <!-- allow custom header slot or fallback to prop -->
        <slot name="title">{{ title }}</slot>
      </span>

      <!-- Show / hide button (optional) -->
      <el-button
          v-if="showToggle"
          class="block-header-adjustments-v1"
          :class="{ active: isExpanded }"
          link
          @click="toggle"
      >
        {{ isExpanded ? hideText : showText }}
        <i class="block-header-dropdown-icon el-icon-arrow-down" />
      </el-button>
    </div>

    <!-- Collapsible content -->
    <Transition name="block-fade-slide" mode="out-in">
      <div v-show="isExpanded">
        <slot />
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

/**
 * Re‑usable card‑layout component.
 * Provides themed background, header & optional collapse toggle.
 */
const props = defineProps({
  /** Заголовок блока (если не используется именованный слот) */
  title: { type: String, default: '' },
  /** Показать кнопку свернуть/развернуть */
  showToggle: { type: Boolean, default: true },
  /** Текст при скрытом контенте */
  showText: { type: String, default: 'Показать больше' },
  /** Текст при раскрытом контенте */
  hideText: { type: String, default: 'Скрыть' },
  /** Центрировать заголовок */
  centerTitle: { type: Boolean, default: false }
})

const isExpanded = ref(!props.showToggle) // открыто по умолчанию, если выключен toggle

watch(() => props.showToggle, (val) => {
  if (!val) isExpanded.value = true
})

function toggle () {
  isExpanded.value = !isExpanded.value
}
</script>

<style scoped>
@import "@/assets/styles/BlockCard.css";

/*.block-v1, .block-header-v1, etc. уже определены в BlockCard.css*/
.block-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-heading);
}

/* центрирование заголовка при необходимости */
.block-header-v1.centered {
  justify-content: center;
}
</style>
