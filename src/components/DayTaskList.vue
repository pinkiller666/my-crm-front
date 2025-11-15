<template>
  <el-timeline class="tasks-timeline">
    <el-timeline-item
        v-for="(task, index) in tasks"
        :key="task.id"
        :hide-timestamp="true"
        placement="top"
    >
      <!-- Вставляем наш новый презентационный компонент -->
      <DayTaskItem
          :task="task"
          @completeTask="(taskArg, val) => toggleTaskComplete(taskArg, val)"
          @editTask="(taskArg) => editTask(taskArg)"
          @removeTask="(taskArg) => removeTask(taskArg)"
      />
    </el-timeline-item>
  </el-timeline>
</template>

<script setup>
import DayTaskItem from './DayTaskItem.vue'

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits([
  'removeTask',
  'completeTask',
  'editTask'
])

function getEvent(task) {
  if (!task) return null
  if ('event' in task) return task.event
  return null
}

// ---- проброс событий наружу (без изменений) ----
function toggleTaskComplete(task, isChecked) {
  emit('completeTask', task, isChecked)
}
function editTask(task) {
  emit('editTask', task)
}
function removeTask(task) {
  emit('removeTask', task)
}

</script>


<style>
.el-timeline{
  padding: 0;
}
</style>

<style scoped>
.tasks-timeline{
  margin-left: 1em;
}
</style>