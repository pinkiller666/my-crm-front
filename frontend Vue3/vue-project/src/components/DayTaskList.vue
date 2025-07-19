<template>
  <div
      class="task-list-wrapper"
      ref="root"
      @mouseenter="showLongConnector"
      @mouseleave="hideLongConnector"
  >
    <OneTaskBlock
        v-for="(task, index) in localTasks"
        :key="task.id"
        ref="taskRefs"
        :task="task"
        :is-first="index === 0"
        :is-last="index === localTasks.length - 1"
        @deleteTask="removeTask"
    />
    <div class="hover-zone"></div>
    <el-button type="primary" :icon="Plus" circle class="my-button" @click="taskAdd"/>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import OneTaskBlock from './OneTaskBlock.vue'
import { Plus } from '@element-plus/icons-vue'
import type { ComponentPublicInstance } from 'vue'

const root = ref<HTMLElement | null>(null)
const firstTaskRef = ref<ComponentPublicInstance<{ showLongConnector: () => void, hideLongConnector: () => void }> | null>(null)


const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  }
})

// 🔁 Локальная копия задач, чтобы можно было мутировать
const localTasks = ref([...props.tasks])

function showLongConnector() {
  firstTaskRef.value?.showLongConnector?.()
}
function hideLongConnector() {
  firstTaskRef.value?.hideLongConnector?.()
}

function removeTask(taskId: number) {
  const index = localTasks.value.findIndex(t => t.id === taskId)
  if (index !== -1) {
    localTasks.value.splice(index, 1)
    // 💡 здесь можно будет вызвать goLower и пересчитать смещение
  }
}

function taskAdd() {
  // заглушка — позже добавим интерфейс
  const newId = Math.max(...localTasks.value.map(t => t.id), 0) + 1
  localTasks.value.push({
    id: newId,
    title: 'Новая задача',
    status: 'default'
  })
}
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
  pointer-events: auto;
  margin-top: -0.7rem;
}

.task-list-wrapper:hover {
  background-color: unset;
}

.task-list-wrapper .my-button {
  opacity: 0;
  pointer-events: none;
  position: absolute;
  left: -1em;
  bottom: -1em;
  z-index: 50;
  transition: opacity 0.5s ease;
}

.hover-zone {
  position: absolute;
  width: 5em;
  height: 5em;
  left: -2em;
  bottom: -2em;
  z-index: 49;
  /* визуально не видно, но работает */
}

.task-list-wrapper:hover .my-button {
  opacity: 1;
  pointer-events: auto;
}
</style>
