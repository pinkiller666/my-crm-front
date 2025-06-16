<template>
  <div class="block-carousel">
    <el-button @click="goLeft" :icon="ArrowLeft" circle />

    <div class="carousel-left" v-if="hasPrev">
      {{ getLabel(prevIndex) }}
    </div>

    <div class="carousel-center">
      {{ getLabel(currentIndex) }}
    </div>

    <div class="carousel-right" v-if="hasNext">
      {{ getLabel(nextIndex) }}
    </div>

    <el-button @click="goRight" :icon="ArrowRight" circle />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: [String, Number],
    required: true,
  },
  labelField: {
    type: String,
    default: 'label',
  },
  keyField: {
    type: String,
    default: 'value',
  },
})

const emit = defineEmits(['update:modelValue'])

const currentIndex = computed(() =>
    props.items.findIndex(item => item[props.keyField] === props.modelValue)
)

const getLabel = index => props.items[index]?.[props.labelField] || ''

const prevIndex = computed(() =>
    (currentIndex.value - 1 + props.items.length) % props.items.length
)

const nextIndex = computed(() =>
    (currentIndex.value + 1) % props.items.length
)

const hasPrev = computed(() => props.items.length > 1)
const hasNext = computed(() => props.items.length > 1)

function goLeft() {
  emit('update:modelValue', props.items[prevIndex.value][props.keyField])
}

function goRight() {
  emit('update:modelValue', props.items[nextIndex.value][props.keyField])
}
</script>

<style scoped>
.block-carousel {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  position: relative;
  overflow: hidden;
  min-height: 2.5rem;
  margin-bottom: 1rem;
}

.carousel-center {
  font-size: 1.2rem;
  font-weight: 600;
  opacity: 1;
  transform: scale(1);
  transition: all 0.3s ease;
  color: var(--text-main);
}

.carousel-left,
.carousel-right {
  font-size: 1rem;
  opacity: 0.4;
  transform: scale(0.9);
  transition: all 0.3s ease;
  color: color-mix(in srgb, var(--text-main) 40%, var(--bg-main) 60%);
}
</style>
