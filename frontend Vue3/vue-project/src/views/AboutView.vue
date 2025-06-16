<template>
  <div class="about-demo">
    <h2>Демонстрация DayPair с задачами</h2>
    <div class="example-wrapper">
      <DayPair
          v-for="(entry, index) in demoDayPairs"
          :key="entry.date"
          v-bind="entry"
          :ref="el => setDayPairRef(el, index)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import DayPair from '@/components/DayPair.vue'

const demoDayPairs = [
  {
    day: 15,
    weekday: 'Ср',
    date: '2025-06-15',
    type: 'work',
    tasks: [
      { id: 1, title: 'Купить молоко и творог и новую собаку и муку и батон и синюю краску', status: 'default' },
      { id: 2, title: 'Погладить кота', status: 'completed' },
      { id: 3, title: 'Записаться к врачу и еще к врачу, ко всем нахуй врачам в мире, к доктору Хаосу и Айбалиту', status: 'overdue' }
    ]
  },
  {
    day: 16,
    weekday: 'Чт',
    date: '2025-06-16',
    type: 'work',
    tasks: [
      { id: 4, title: 'Выгулять пыль и извиниться перед пылесосом', status: 'default' },
      { id: 5, title: 'Сварить макароны, но без воды, без смысла, без плана', status: 'overdue' },
      { id: 6, title: 'Позвонить кошке. Узнать, где она прячет мои силы', status: 'default' },
      { id: 7, title: 'Оформить визу в спокойствие и не вернуться обратно', status: 'completed' },
      { id: 8, title: 'Перевести утюг в авиарежим и лечь спать', status: 'default' }
    ]
  }
]

const dayPairRefs = ref<any[]>([])

function setDayPairRef(el: any, index: number) {
  if (el) {
    dayPairRefs.value[index] = el
  }
}

function resolveOverlap(i: number) {
  const current = dayPairRefs.value[i]?.taskList
  const prev = dayPairRefs.value[i - 1]?.taskList?.root

  if (current?.goLower && prev) {
    const height = prev.getBoundingClientRect().height
    console.log(`👇 Сдвигаем DayTaskList для элемента ${i} на высоту предыдущего (${height}px)`)
    current.goLower(height)
  }
}

function checkIntersections() {
  console.log('функция checkIntersections запустилась')
  console.log('Длина массива дней:', dayPairRefs.value.length)
  for (let i = 1; i < dayPairRefs.value.length; i++) {
    console.log('запустился первый цикл')
    const current = dayPairRefs.value[i]?.taskList?.root
    const prev = dayPairRefs.value[i - 1]?.taskList?.root

    if (!current || !prev) continue

    const currentRect = current.getBoundingClientRect()
    const prevRect = prev.getBoundingClientRect()

    const horizontalOverlap = !(currentRect.left > prevRect.right || currentRect.right < prevRect.left)
    const verticalOverlap = !(currentRect.top > prevRect.bottom || currentRect.bottom < prevRect.top)

    if (horizontalOverlap && verticalOverlap) {
      console.warn(`\u{1F534} Пересечение между ${i - 1} и ${i}`)
      resolveOverlap(i)
    } else {
      console.log(`\u2705 Нет пересечений: ${i - 1} vs ${i}`)
    }
  }
}

onMounted(() => {
  nextTick(() => {
    requestAnimationFrame(() => {
      checkIntersections()
    })
  })
})

</script>

<style>
.about-demo {
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2rem;
  padding: 3rem 1rem;
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 16px;
  align-items:center;
}

.about-demo h2 {
  color: var(--color-primary, #409eff);
  margin-bottom: 1rem;
  font-size: 2rem;
  font-weight: 700;
}

.example-wrapper {
  flex-direction: row;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  justify-content: center;
}
</style>
