<template>
  <transition
      @before-enter="beforeEnter"
      @enter="enter"
      @before-leave="beforeLeave"
      @leave="leave"
      name="expand"
  >
    <div v-show="visible" ref="expandBlock">
      <slot />
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue'

const expandBlock = ref(null)
defineProps({ visible: Boolean })

function beforeEnter(el) {
  el.style.height = '0'
}
function enter(el) {
  el.style.height = el.scrollHeight + 'px'
}
function beforeLeave(el) {
  el.style.height = el.scrollHeight + 'px'
}
function leave(el) {
  el.style.height = '0'
}
</script>

<style scoped>
  .expand-enter-active,
  .expand-leave-active {
    transition: height 0.3s ease, opacity 0.3s ease;
    overflow: hidden;
  }

  .expand-enter-from,
  .expand-leave-to {
    height: 0;
    opacity: 0;
  }

  .expand-enter-to,
  .expand-leave-from {
    height: auto;
    opacity: 1;
  }
</style>
