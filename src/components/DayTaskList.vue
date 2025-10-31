<template>
  <el-timeline class="tasks-timeline">
    <el-timeline-item
      v-for="(task, index) in tasks"
      :key="task.id"
      :timestamp="formatTime(task.event.start_datetime)"
      placement="top"
    >

<div
  class="timeline-task"
  :class="{ cancelled: task.overlay?.status === 'cancelled' }"
>
  <el-dropdown @command="(cmd) => handleDropdownCommand(cmd, task)" trigger="contextmenu">
    <el-checkbox
      :model-value="task.overlay?.is_completed ?? task.event.is_completed"
      :label="task.event.name"
      @change="(val) => toggleTaskComplete(task, val)"
    />

    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="edit">Редактировать</el-dropdown-item>
        <el-dropdown-item command="delete">Удалить</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>


<span v-if="task.event.is_balance_correction">💰</span>
  <span class="task-desc">{{ task.event.description }}</span>
<AmountNumber v-if="task.event.account" :amount="task.event.amount" />
</div>
    </el-timeline-item>
  </el-timeline>
</template>


<script setup>
import { Delete, Edit } from '@element-plus/icons-vue'
import { ref, nextTick } from 'vue'
import AmountNumber from './AmountNumber.vue'

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  },
})

const emit = defineEmits([
  'removeTask',
  'completeTask',
  'editTask'
])


function formatTime(datetime) {
  const d = new Date(datetime)
  return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

function toggleTaskComplete(task, isChecked) {
  emit('completeTask', task, isChecked)
}

function editTask(task) {
  emit('editTask', task)
}

function removeTask(task) {
  emit('removeTask', task)
}

function handleDropdownCommand(command, task) {
  if (command === 'edit') editTask(task)
  else if (command === 'delete') removeTask(task)
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

.cancelled {
  opacity: .4;
}
</style>

