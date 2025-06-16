<template>
  <div
      class="task-list-wrapper"
      ref="root"
      :class="{ hovered: anyHovered }"
  >
    <OneTaskBlock
        v-for="(task, index) in tasks"
        :key="task.id"
        :ref="el => setTaskRef(el, index)"
        :task="task"
        :is-first="index === 0"
        :is-last="index === tasks.length - 1"
    />
  </div>
</template>

<script setup lang="ts">
import {ref, computed, nextTick} from 'vue'
import OneTaskBlock from './OneTaskBlock.vue'

const root = ref<HTMLElement | null>(null)

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  }
})

// 📌 refs на все OneTaskBlock
const taskRefs = ref<any[]>([])

function setTaskRef(el: any, index: number) {
  if (el) taskRefs.value[index] = el
}

// ✅ Считаем, есть ли хоть один hovered
const anyHovered = computed(() => {
  return taskRefs.value.some(ref => ref?.hovered?.value)
})

function goLower(offset: number) {
  if (root.value) {
    const current = parseFloat(root.value.style.marginTop || '0')
    root.value.style.marginTop = `${current + offset}px`

    nextTick(() => {
      void root.value?.offsetHeight
    })
  }
}

defineExpose({ root, goLower })
</script>

<style scoped>
.task-list-wrapper {
  z-index: 20;
  display: flex;
  flex-direction: column;
  position: relative;
  padding-left: 0rem;
  align-items: flex-start;
  justify-content: flex-start;
  width: 100%;
  min-height: 100%;
  box-sizing: border-box;
  transition: background-color 0.2s ease;
}

.task-list-wrapper.hovered {
  background-color: #8fd14f;
}
</style>
