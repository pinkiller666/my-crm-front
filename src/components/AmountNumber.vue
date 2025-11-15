<template>
  <span
      v-if="displayText !== null"
      class="amount-number"
      :class="{
      'amount-positive': isPositive,
      'amount-negative': isNegative
    }"
  >
    {{ displayText }}
  </span>
</template>

<script>
export default {
  name: 'AmountNumber',
  props: {
    amount: {
      type: [Number, String],
      required: true
    }
  },
  computed: {
    numericAmount () {
      let value = this.amount

      if (value === null || typeof value === 'undefined') {
        return null
      }

      if (typeof value === 'string') {
        const parsed = Number(value)
        if (Number.isNaN(parsed)) {
          return null
        }
        value = parsed
      }

      if (typeof value !== 'number' || !Number.isFinite(value)) {
        return null
      }

      return value
    },

    isPositive () {
      return this.numericAmount !== null && this.numericAmount > 0
    },

    isNegative () {
      return this.numericAmount !== null && this.numericAmount < 0
    },

    displayText () {
      if (this.numericAmount === null) {
        return null
      }

      const absValue = Math.abs(this.numericAmount)

      // форматируем с пробелами по разрядам, без копеек
      const formatted = new Intl.NumberFormat('ru-RU', {
        maximumFractionDigits: 0,
        minimumFractionDigits: 0
      }).format(absValue)

      // доходы: "+ 10 000"
      if (this.numericAmount > 0) {
        return '+ ' + formatted
      }

      // расходы: "3 500" (БЕЗ минуса)
      if (this.numericAmount < 0) {
        return formatted
      }

      // ноль: просто "0"
      return '0'
    }
  }
}
</script>

<style scoped>
.amount-number {
  font-weight: 500; /* такой же вес, как хотим у времени */
}

/* доходы — зелёные */
.amount-positive {
  color: #32b36b;
}

/* расходы — серые */
.amount-negative {
  color: #666666;
}
</style>
