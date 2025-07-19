<!--
  Компонент OneTaskBlock
  — отрисовывает одну задачу со стилями «вертикальная линия + углы»
  Props:
    • task: { id, title, status } — данные задачи
    • isFirst: Boolean — первый ли это элемент в списке
    • isLast: Boolean — последний ли элемент
  Emits:
    • deleteTask(id: number) — пользователь нажал кнопку удаления
  Логика:
    • при монтировании измеряет высоту текста → в --text-block-height
    • при hover показывает кнопки действий
    • при клике «галочка» переключает локальный флаг isCompleted
    • при клике «мусорка» бросает emit('deleteTask', id)
-->

<template>
  <div class="task-wrapper" :class="{ 'first-block': isFirst }">
    <div class="line-zone">
      <div
          class="task-row"
          :style="{ '--text-block-height': textBlockHeight }"
      >
        <!-- Если последний — рисуем уголок -->
        <div v-if="isLast" class="vertical-corner-line"></div>
        <div v-if="isLast" class="corner-line"></div>

        <!-- Иначе — обычные линии -->
        <template v-else>
          <template v-if="!isFirst">
            <div class="vertical main"></div>
          </template>
          <template v-else>
            <div class="vertical-first"></div>
          </template>
          <div class="horizontal"></div>
        </template>

        <div class="task-and_actions-wrapper">
          <div ref="contentRef" class="task-content" :class="{ completed: isCompleted }">
            {{ task.title }}
          </div>
          <div class="task-actions">
            <el-button type="success" :icon="Check" size="small" circle class="my-button" @click="toggleTaskComplete"/>
            <el-button type="primary" :icon="Edit" size="small" circle class="my-button" @click="taskEdit"/>
            <el-button type="danger" :icon="Delete" size="small" circle class="my-button" @click="taskDelete"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { Check, Delete, Edit } from '@element-plus/icons-vue'

const props = defineProps({
  task: { type: Object, required: true },
  isFirst: { type: Boolean, default: false },
  isLast: { type: Boolean, default: false },
})

const contentRef = ref(null)
const textBlockHeight = ref('auto')
const isCompleted = ref(false)
const emit = defineEmits(['deleteTask'])

onMounted(() => {
  nextTick(() => {
    if (contentRef.value) {
      const height = contentRef.value.offsetHeight
      textBlockHeight.value = `${height}px`
      // console.log('Текущая высота task-content:', textBlockHeight.value)
    }
  })
})

function toggleTaskComplete() {
  isCompleted.value = !isCompleted.value
}
function taskDelete() {
  emit('deleteTask', props.task.id)
}
function taskEdit() {
  // Пока пусто — добавишь свою логику
}
</script>

<style scoped>
.task-wrapper {
  min-height: unset;
  margin: 0;
  padding: 0;
  display: flex;
  align-items: flex-start;
  position: relative;
  left: 0;
  border: 0px solid #0c54ef;
  z-index: 30;
}

/* Синяя длинная палка — только у первого блока */
.task-wrapper.first-block .line-zone::before {
  content: '';
  position: absolute;
  left: 0px;   /* Подбери так, чтобы совпало с серым кружком */
  top: 0;
  width: 4px;
  height: 210px; /* Подбери под свои задачи! */
  transform: translateY(-100px);
  background: var(--color-primary, #0c54ef);
  z-index: 99;
  opacity: 1;
}
.line-zone {
  position: relative;
  background: rgba(0,0,255,0.05); /* временно для визуализации */
}

.vertical {
  min-width: 2px;
  width: 2px;
  background-color: var(--color-primary);
  position: relative;
}
.vertical-first {
  min-width: 2px;
  width: 2px;
  align-self: stretch;
  margin-top: calc(var(--padding-after-content) * -1);
  position: relative;
  left: 0;
  background: linear-gradient(to bottom, transparent 0%, transparent 10%, var(--color-primary) 50%);
}
.vertical.upper {
  height: 1.75rem;
  background-color: #8fd14f;
}
.vertical.main {
  min-width: 2px;
  width: 2px;
  align-self: stretch;
  margin-top: calc(var(--padding-after-content) * -1);
  position: relative;
  left: 0;
}
.vertical.lower {
  height: 1rem;
}
.horizontal {
  position: absolute;
  width: 1rem;
  height: 2px;
  background-color: var(--color-primary);
  top: calc((100% - var(--padding-after-content)) / 2 + var(--padding-after-content));
  transform: translateY(-50%);
}

.task-row {
  margin: 0;
  box-sizing: border-box;
  display: flex;
  gap: 1rem;
  align-items: stretch;
  border: 0px solid black;
  position: relative;
  padding-top: var(--padding-after-content);
  left: 0;
  padding-right: 0em;
}
.task-content {
  font-size: 0.7rem;
  color: var(--text-main);
  min-width: 200px;
  max-width: 240px;
  display: flex;
  align-items: center;
  margin-left: 0.5rem;
  border-bottom: 1px dashed rgba(0,0,0,0.2);
  border-top: 1px dashed rgba(0,0,0,0.2);
  padding: 0.25rem 0.5rem;
  white-space: normal;
  word-break: break-word;
  max-width: 100%;
}
.task-content:hover {
  text-shadow: 0 0 1px var(--color-primary);
  background-color: rgba(255, 192, 203, 0.0);
}
.vertical-corner-line {
  position: relative;
  width: 2px;
  max-width: 2px;
  min-width: 2px;
  height: calc(var(--text-block-height) / 2);
  background-color: var(--color-primary);
  margin-right: 0;
  margin-top: calc(var(--padding-after-content) * -1);
  z-index: 999;
}
.corner-line {
  position: absolute;
  width: 1rem;
  border-left: 2px solid var(--color-primary);
  border-bottom: 2px solid var(--color-primary);
  border-bottom-left-radius: 10px;
  left: 0;
  top: 0;
  margin-top: 1rem;
  height: calc(var(--text-block-height) / 2);
}
.vertical, .horizontal {
  pointer-events: none;
}
.my-button {
  z-index: 50;
}
.task-actions {
  opacity: 0;
  pointer-events: none;
  transition: .5s;
  display: flex;
  gap: .4rem;
  right: 0;
  position: absolute;
  transform: translateX(100%);
}
.task-row:hover .task-actions {
  opacity: 1;
  pointer-events: auto;
}
.task-and_actions-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.task-content.completed {
  text-decoration: line-through;
  opacity: 0.6;
}
</style>

<style>
:root {
  --padding-after-content: 1rem;
  --tail-length: 1rem;
}
</style>
