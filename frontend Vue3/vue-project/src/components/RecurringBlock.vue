<template>
  <div class="recurring-block">
    <el-date-picker
        v-model="form.dateStart"
        type="date"
        placeholder="Дата начала"
        class="input-field"
    />
    <el-date-picker
        v-model="form.dateEnd"
        type="date"
        placeholder="Дата окончания"
        class="input-field"
    />
    <!-- Здесь позже можно вставить recurrence picker -->
  </div>
</template>

<script setup>
defineProps({
  form: Object
})
</script>

<style scoped>
.recurring-block {
  padding: 1rem; /* Добавляем внутренний отступ */
}

.input-field {
  margin-bottom: 1rem;
}
</style>
