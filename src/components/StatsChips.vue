<template>
  <div class="chips-wrap">
    <div class="chip chip-workdays">
      <span class="chip-num">{{ summary.work_days }}</span>
      <span class="chip-text">рабочих дней</span>
    </div>

    <div class="chip chip-hours">
      <span class="chip-num">{{ summary.work_hours_total }}</span>
      <span class="chip-text">рабочих часов</span>
    </div>

    <div class="chip chip-offdays">
      <span class="chip-num">{{ summary.off_days }}</span>
      <span class="chip-text">выходных</span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  summary: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.chips-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  padding: 20px 0;
  margin-bottom: 0px;
}

/* Общий стиль чипов — делаем воздушнее */
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;

  padding: 4px 10px;        /* было 6px 12px — уменьшено */
  border-radius: 10px;      /* чуть меньше скругление */
  border: 1px solid rgba(0,0,0,0.08); /* тонкая, ненавязчивая рамка */

  font-size: 0.82rem;       /* меньше текст */
  line-height: 1;
  background: #fffbe6;      /* мягче, чем старый жёлтый */
  box-shadow: 0 1px 1px rgba(0,0,0,0.05);
}

.chip .chip-num {
  font-weight: 200 !important;         /* было 700 — слишком кричало */
  color: #444;
  opacity: .7;
}

.chip .chip-text {
  opacity: .7;              /* мягче */
  color: #444;
}

/* Персональные цвета — тоже мягче */
.chip-workdays {
  background: #fff6d1;      /* мягкий жёлтый */
}

.chip-hours {
  background: #ffefc2;      /* чуть интенсивнее */
}

.chip-offdays {
  background: #e6f8e0;      /* мягкий зелёный вместо кислотного */
}

</style>
