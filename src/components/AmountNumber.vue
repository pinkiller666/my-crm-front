<template>
  <span
    :class="amountClass"
  >
    {{ formattedAmount }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  amount: {
    type: [Number, String],
    required: true
  }
})


const formattedAmount = computed(() => {
  const amt = Number(props.amount) || 0
  if (amt > 0) return `+${amt.toFixed(2)}`
  if (amt < 0) return `${amt.toFixed(2)}`
  return '0.00'
})

const amountClass = computed(() => {
  const amt = Number(props.amount) || 0
  if (amt > 0) return 'green-amount'
  if (amt < 0) return 'red-amount'
  return ''
})
</script>

<style scoped>
.green-amount {
  color: green;
}

.red-amount {
  color: red;
}

.task-amount {
  font-weight: bold;
}
</style>
