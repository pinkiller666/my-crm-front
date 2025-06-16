<template>
  <div class="task-wrapper" @mouseenter="onEnter" @mouseleave="onLeave">
    <!-- 📏 Визуальная линия: вертикальная + горизонтальная -->
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

        <div ref="contentRef" class="task-content">
          {{ task.title }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';

const props = defineProps({
  task: {
    type: Object,
    required: true
  },
  isFirst: {
    type: Boolean,
    default: false
  },
  isLast: {
    type: Boolean,
    default: false
  }
})

const contentRef = ref(null)
const textBlockHeight = ref('auto')

onMounted(() => {
  nextTick(() => {
    if (contentRef.value) {
      const height = contentRef.value.offsetHeight
      textBlockHeight.value = `${height}px`
      console.log('Текущая высота task-content:', textBlockHeight.value)
    }
  })
})

const hovered = ref(false)

const onEnter = () => {
  console.log('🟢 Навели на OneTaskBlock с задачей:', props.task.title)
  hovered.value = true
}
const onLeave = () => {
  console.log('⚪️ Увели курсор с OneTaskBlock с задачей:', props.task.title)
  hovered.value = false
}

defineExpose({
  hovered
})

</script>

<style scoped>

.task-wrapper {
  min-height: unset;   /* убираем минимум высоты */
  margin: 0;           /* обнуляем внешние отступы */
  padding: 0;
  display: flex;
  align-items: flex-start;
  position: relative;
  left: 0;
  border: 0px solid #0c54ef;
  z-index: 30;
}
.task-wrapper:hover {
  background-color: #8c6c00;
}

.line-zone {
  min-height: unset;   /* убираем минимум высоты */
  margin: 0;           /* обнуляем внешние отступы */
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 0rem;
  border: 0px solid #ef0c49;
  left: 0;
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
  display: flex;
  align-items: stretch;
  border: 0px solid black;
  position: relative;
  padding-top: var(--padding-after-content);
  left: 0;
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
  box-sizing: border-box;
}

.task-content:hover {
  text-shadow: 0 0 1px var(--color-primary);
  background-color: pink;
}

.vertical-corner-line {
  position: relative;
  width: 4px;
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
  margin-top: 1rem; /* убираем отрицательный margin */
  height: calc(var(--text-block-height) / 2);
}

.vertical,
.horizontal {
  pointer-events: none;
}

</style>

<style>
  :root {
    --padding-after-content: 1rem;
    --tail-length: 1rem;
  }

</style>