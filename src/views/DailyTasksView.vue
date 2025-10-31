<template>
  <div>
    <!-- Фильтры -->
    <el-row class="mb-4" type="flex" align="middle" :gutter="10">
      <el-col>
        <el-date-picker
          v-model="selectedDay"
          type="date"
          placeholder="Выберите день"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="onDayChange"
        ></el-date-picker>
      </el-col>
      <el-col>
        <el-button
          :type="typeFilter.size === typeOptions.length || typeFilter.size === 0 ? 'primary' : 'default'"
          @click="toggleAlltypes"
        >
          Все
        </el-button>
      </el-col>
      <el-col v-for="e in typeOptions" :key="e">
        <el-button
          :type="typeFilter.has(e) ? 'primary' : 'default'"
          @click="toggletype(e)"
        >
          {{ e }}
        </el-button>
      </el-col>
      <el-col>
        <el-radio-group v-model="statusFilter">
          <el-radio-button value="all">Все</el-radio-button>
          <el-radio-button value="done">Сделано</el-radio-button>
          <el-radio-button value="not_done">Не сделано</el-radio-button>
        </el-radio-group>
      </el-col>
    </el-row>

    <!-- Заголовок и форма -->
    <div class="section-head">
      <h2>📌 Ваши задачи</h2>
      <el-button circle @click="showForm = !showForm">➕</el-button>
    </div>

    <el-card v-if="showForm" class="mb-4">
      <el-form :model="draft">
        <el-form-item>
          <el-input v-model.trim="draft.name" placeholder="Текст задачи (1–2 предложения)"></el-input>
        </el-form-item>

        <el-form-item>
          <el-select v-model="draft.type" placeholder="Выберите эмодзи">
            <el-option v-for="e in typeOptions" :key="e" :label="e" :value="e"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="draft.with_person">Требует другого человека</el-checkbox>
          <el-checkbox v-model="draft.with_wait">Нужно подождать</el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitTask">Добавить</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Список задач -->
    <el-card>
      <div v-if="filteredTasks.length">
        <el-row v-for="t in filteredTasks" :key="t.id" type="flex" align="middle" class="mb-2">
          <el-col :span="1">
            <el-checkbox
  :model-value="t.overlay?.is_completed ?? t.event.is_completed"
  @change="(val) => handleCompleteTask(t, val)"
  :label="t.event.name"
></el-checkbox>

          </el-col>
          <el-col :span="18">
            <span :class="{done: t.event.is_completed}">{{ t.type }}</span>
            <span v-if="t.with_person">👤</span>
            <span v-if="t.with_wait">⏳</span>
          </el-col>
          <el-col :span="5">
            <el-button text @click="startEdit(t)">📝</el-button>
            <el-button  text @click="handleRemoveTask(t)">❌</el-button>
          </el-col>
        </el-row>
      </div>
      <div v-else class="text-muted">Нет задач по текущим фильтрам.</div>
    </el-card>
  </div>

    <!-- Редактирование -->
    <el-dialog v-model="editing" title="Редактировать задачу">
      <el-form :model="editBuf">
        <el-form-item label="Текст">
          <el-input v-model="editBuf.event.name"></el-input>
        </el-form-item>
        <el-form-item label="Эмодзи">
          <el-select v-model="editBuf.event.type" placeholder="Выберите эмодзи">
            <el-option v-for="e in typeOptions" :key="e" :label="e" :value="e"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="editBuf.event.with_person">Требует другого человека</el-checkbox>
          <el-checkbox v-model="editBuf.event.with_wait">Нужно подождать</el-checkbox>
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="cancelEdit">Отмена</el-button>
        <el-button type="primary" @click="applyEdit">Сохранить</el-button>
      </span>
    </el-dialog>

</template>

<script>
import axios from '@/axios'
import { ref, reactive, computed, watch } from 'vue'

export default {
    props: { date: String },
  emits: ['addTask'],
  setup(props, { emit }) {
    const showForm = ref(false)
    const typeOptions = ['fun', 'routine', 'important', 'gross']
    const typeFilter = ref(new Set())
    const statusFilter = ref('all')
    const tasks = ref([])
    const editing = ref(false)
    const editBuf = reactive({ id: null, name: '', type: '', with_person: false, with_wait: false })
    const draft = reactive({ name: '', type: '', with_person: false, with_wait: false })

    // Выбор дня
    const selectedDay = ref(new Date().toISOString().slice(0, 10)) // по умолчанию сегодня
    const currentMonth = ref(new Date().getMonth() + 1)
    const currentYear = ref(new Date().getFullYear())

const filteredTasks = computed(() => {
  return tasks.value.filter(t => {
    const taskDate = (t.datetime ?? t.event.start_datetime).slice(0, 10)
    const isCompleted = t.overlay?.is_completed ?? t.event.is_completed

    return taskDate === selectedDay.value &&
      (typeFilter.value.size === 0 || typeFilter.value.has(t.event.type)) &&
      (statusFilter.value === 'all' ||
       (statusFilter.value === 'done' && isCompleted) ||
       (statusFilter.value === 'not_done' && !isCompleted))
  })
})


    const toggletype = (e) => {
      if (typeFilter.value.has(e)) typeFilter.value.delete(e)
      else typeFilter.value.add(e)
      typeFilter.value = new Set(typeFilter.value)
    }
    const toggleAlltypes = () => {
      if (typeFilter.value.size === typeOptions.length) typeFilter.value = new Set()
      else typeFilter.value = new Set(typeOptions)
    }

    const loadAllEvents = async () => {
      try {
        const resp = await axios.get(`/api/schedule/all_events/?year=${currentYear.value}&month=${currentMonth.value}`)
        tasks.value = resp.data
      } catch (err) { console.error(err) }
    }

    const onDayChange = (day) => {
      const [y, m] = day.split('-')
      if (+y !== currentYear.value || +m !== currentMonth.value) {
        currentYear.value = +y
        currentMonth.value = +m
        loadAllEvents()
      }
    }

    const submitTask = async () => {
      if (!draft.name) return
      try {
        const payload = {
          name: draft.name,
          description: '',
          start_datetime: new Date(selectedDay.value).toISOString(),
          type: draft.type,
          with_person: draft.with_person,
          with_wait: draft.with_wait
        }
        const response = await axios.post('/api/schedule/events/', payload)
        tasks.value.unshift({'event': response.data})
        Object.assign(draft, { name: '', type: '', with_person: false, with_wait: false })
        showForm.value = false
      } catch (err) { console.error('Ошибка при добавлении задачи:', err) }
    }
const handleCompleteTask = async (task, newStatus) => {
  try {
    const payload = {
      status: newStatus ? 'complete' : 'incomplete',
      is_completed: newStatus,
      instance_datetime: task.datetime,
    }

    if (task.is_recurring) {
      await axios.patch(`/api/schedule/events/${task.event.id}/update-status/`, payload)
      // обновляем локально overlay для конкретного вхождения
      const idx = tasks.value.findIndex(t => t.id === task.id)
      console.log(task.id)
      if (idx !== -1) {
        tasks.value[idx].overlay.is_completed = newStatus
        tasks.value[idx].overlay.status = payload.status
        console.log(tasks.value[idx])
      }
    } else {
      await axios.patch(`/api/schedule/events/${task.event.id}/`, {
        is_completed: newStatus,
        status: payload.status,
      })
      // обновляем локально event
      const idx = tasks.value.findIndex(t => t.id === task.id)
      if (idx !== -1) {
        tasks.value[idx].event.is_completed = newStatus
        tasks.value[idx].event.status = payload.status
      }
    }
  } catch (err) {
    console.error('Не удалось обновить статус:', err)
  }
}


const applyEdit = async () => {
  try {
    const payload = {
      name: editBuf.event.name,
      type: editBuf.event.type,
      with_person: editBuf.event.with_person,
      with_wait: editBuf.event.with_wait
    }
    await axios.patch(`/api/schedule/events/${editBuf.event.id}/`, payload)

    // Патчим локально
    const idx = tasks.value.findIndex(t => t.id === editBuf.id)
    if (idx !== -1) {
      Object.assign(tasks.value[idx], payload)
    }

    editing.value = false
  } catch (err) {
    console.error(err)
  }
}

const handleRemoveTask = async (task) => {
  try {
    if (task.is_recurring) {
      await axios.delete(`/api/schedule/events/${task.event.id}/delete/`, {
        params: { instance_datetime: task.datetime }
      })
    } else {
      await axios.delete(`/api/schedule/events/${task.event.id}/delete/`)
    }
      tasks.value = tasks.value.filter(t => t.id !== task.id)

    console.log(`Task ${task.id} удалена!`)
  } catch (err) {
    console.error('Ошибка при удалении задачи:', err)
  }
}


    const startEdit = (t) => {
      editing.value = true
      Object.assign(editBuf, t)
    }


    const cancelEdit = () => { editing.value = false }


    loadAllEvents()

    return {
      showForm, typeOptions, typeFilter, toggletype, toggleAlltypes,
      statusFilter, tasks, draft, submitTask, filteredTasks,
      selectedDay, onDayChange, editing, editBuf, startEdit, applyEdit, cancelEdit,
      handleCompleteTask, handleRemoveTask
    }
  }
}
</script>
