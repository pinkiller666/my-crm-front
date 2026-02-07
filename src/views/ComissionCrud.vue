<template>
  <div>
    <div style="display:flex; justify-content: space-between; margin-bottom: 16px;">
      <h2>Commissions</h2>
      <el-button type="primary" @click="openCreate">Создать комиссию</el-button>
    </div>

    <el-table
        :data="commissions"
        v-loading="loading"
        size="small"
        style="width: 100%;"
    >
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="Название" width="200" />
      <el-table-column prop="artist_name" label="Артист" width="180" />
      <el-table-column prop="commissioner_name" label="Заказчик" width="180" />
      <el-table-column prop="amount" label="Сумма" width="120">
        <template #default="{ row }">
          {{ row.amount }} {{ row.currency }}
        </template>
      </el-table-column>
      <el-table-column prop="accepted_at" label="Принято" width="140" />
      <el-table-column label="Действия" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">Редакт.</el-button>
          <el-button size="small" type="danger" @click="confirmDelete(row)">
            Удалить
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
        v-model="dialogVisible"
        :title="isEdit ? 'Редактировать комиссию' : 'Создать комиссию'"
        width="600px"
    >
      <el-form :model="form" label-position="top" :disabled="saving">
        <el-form-item label="Название">
          <el-input v-model="form.name" placeholder="Название комиссии (опционально)" />
        </el-form-item>

        <el-form-item label="Артист">
          <el-select
              v-model="form.artist"
              placeholder="Артист"
              :disabled="artists.length <= 1"
          >
            <el-option
                v-for="a in artists"
                :key="a.id"
                :label="a.display_name"
                :value="a.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Commissioner ID">
          <!-- если есть API для commissioner – тут можно тоже сделать селект -->
          <el-input
              v-model.number="form.commissioner"
              placeholder="ID заказчика"
          />
        </el-form-item>

        <el-form-item label="Сумма">
          <el-input-number
              v-model="form.amount"
              :min="0"
              :step="1"
              style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="Валюта">
          <el-select v-model="form.currency">
            <el-option label="USD" value="USD" />
            <el-option label="EUR" value="EUR" />
            <el-option label="RUB" value="RUB" />
            <!-- добавь свои currency_choices при необходимости -->
          </el-select>
        </el-form-item>

        <!-- Референс-изображения для комиссии -->
        <el-form-item label="Референсы (рефы / позы / палитра / мудборд)">
          <div class="refs-wrapper">
            <!-- Upload button for multiple images -->
            <el-upload
                class="refs-upload"
                list-type="picture-card"
                :auto-upload="false"
                :multiple="true"
                :show-file-list="false"
                accept=".jpg,.jpeg,.png,.webp"
                :on-change="handleRefFilesChange"
            >
              <el-icon><Plus /></el-icon>
              <template #tip>
                <div style="font-size: 12px; color: #999; margin-top: 4px;">
                  Можно загрузить несколько изображений. Поддерживаются: jpg, jpeg, png, webp.
                </div>
              </template>
            </el-upload>

            <!-- List of reference images with details -->
            <div v-if="referenceImages.length" class="refs-list">
              <div
                  v-for="refImg in referenceImages.filter(r => !r.isDeleted)"
                  :key="refImg.uid || refImg.id"
                  class="ref-item"
              >
                <div class="ref-thumb">
                  <el-image
                      v-if="refImg.previewUrl"
                      :src="refImg.previewUrl"
                      style="width:100%; height:100%; object-fit:cover; border-radius:4px;"
                      :preview-src-list="[refImg.previewUrl]"
                  />
                </div>

                <div class="ref-fields">
                  <div class="ref-fields-row">
                    <el-select
                        v-model="refImg.kind"
                        placeholder="Тип"
                        style="width: 160px;"
                    >
                      <el-option
                          v-for="opt in REFERENCE_KIND_OPTIONS"
                          :key="opt.value"
                          :label="opt.label"
                          :value="opt.value"
                      />
                    </el-select>

                    <el-input-number
                        v-model="refImg.order"
                        :min="0"
                        :step="1"
                        controls-position="right"
                        style="width: 110px;"
                        placeholder="Порядок"
                    />
                  </div>

                  <el-input
                      v-model="refImg.caption"
                      placeholder="Подпись / комментарий"
                      size="small"
                      style="margin-top: 6px;"
                  />

                  <el-input
                      v-model="refImg.source_url"
                      placeholder="Ссылка на источник (опционально)"
                      size="small"
                      style="margin-top: 6px;"
                  />

                  <div class="ref-actions">
                    <el-button
                        type="danger"
                        size="small"
                        text
                        @click="removeReference(refImg)"
                    >
                      Удалить
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <div v-else style="font-size: 12px; color: #999; margin-left: 4px;">
              Пока нет референсов. Загрузите изображения, чтобы добавить их.
            </div>
          </div>
        </el-form-item>

        <el-form-item label="Описание">
          <el-input
              type="textarea"
              v-model="form.description"
              :rows="3"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false" :disabled="saving">Отмена</el-button>
        <el-button type="primary" @click="submitForm" :loading="saving">
          Сохранить
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from '@/axios'
import { useArtworkOptions } from '@/composables/useArtworkOptions'
import { Plus } from '@element-plus/icons-vue'

const commissions = ref([])
const loading = ref(false)
const saving = ref(false)

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)

const { artists, fetchArtists } = useArtworkOptions()

const emptyForm = () => ({
  id: null,
  name: '',
  artist: null,
  commissioner: null,
  amount: 0,
  currency: 'USD',
  description: ''
})

const form = ref(emptyForm())

// ----------------- REFS STATE -----------------
const referenceImages = ref([])
// Структура элемента:
// {
//   id?: number           // для уже существующих на сервере
//   uid: string           // локальный идентификатор
//   file?: File | null    // новый файл
//   previewUrl: string    // URL для превью
//   kind: string          // 'ref' | 'pose' | 'color' | 'mood' | 'other'
//   caption: string
//   source_url: string
//   order: number
//   isNew: boolean        // новый
//   isDeleted: boolean    // помечен на удаление
// }

const REFERENCE_KIND_OPTIONS = [
  { value: 'ref', label: 'Референс' },
  { value: 'pose', label: 'Поза' },
  { value: 'color', label: 'Цвет/палитра' },
  { value: 'mood', label: 'Мудборд' },
  { value: 'other', label: 'Другое' }
]

const handleRefFilesChange = (file) => {
  const raw = file.raw
  if (!raw) return

  const uid = file.uid || `${Date.now()}-${Math.random().toString(36).slice(2)}`

  referenceImages.value.push({
    id: null,
    uid,
    file: raw,
    previewUrl: URL.createObjectURL(raw),
    kind: 'ref',
    caption: '',
    source_url: '',
    order: referenceImages.value.length,
    isNew: true,
    isDeleted: false
  })
}

const removeReference = (item) => {
  const idx = referenceImages.value.findIndex(
      (r) => r.uid === item.uid || (item.id && r.id === item.id)
  )
  if (idx === -1) return

  const ref = referenceImages.value[idx]
  if (ref.id && !ref.isNew) {
    // Уже существует на сервере – помечаем как удалённый
    ref.isDeleted = true
  } else {
    // Новый, ещё не сохранённый – убираем из массива
    referenceImages.value.splice(idx, 1)
  }
}

const loadReferences = async (commissionId) => {
  if (!commissionId) {
    referenceImages.value = []
    return
  }

  try {
    const { data } = await axios.get(`/artworks/commissions/${commissionId}/references/`)
    referenceImages.value = (data || []).map((item) => ({
      id: item.id,
      uid: `existing-${item.id}`,
      file: null,
      previewUrl: item.image_url, // или item.image, зависит от API
      kind: item.kind || 'ref',
      caption: item.caption || '',
      source_url: item.source_url || '',
      order: typeof item.order === 'number' ? item.order : 0,
      isNew: false,
      isDeleted: false
    }))
  } catch (err) {
    console.error(err)
    ElMessage.error('Не удалось загрузить референсы комиссии')
  }
}

// ----------------- API -----------------

const fetchCommissions = async () => {
  loading.value = true
  try {
    const { data } = await axios.get('/artworks/commissions/')
    commissions.value = data
  } catch (e) {
    console.error(e)
    ElMessage.error('Не удалось загрузить комиссии')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    fetchCommissions(),
    fetchArtists()
  ])

  // если артист один – подставим его сразу при создании
  if (artists.value.length === 1) {
    form.value.artist = artists.value[0].id
  }
})

const openCreate = () => {
  isEdit.value = false
  editingId.value = null
  form.value = emptyForm()
  referenceImages.value = []
  dialogVisible.value = true
}

const openEdit = async (row) => {
  isEdit.value = true
  editingId.value = row.id
  form.value = {
    id: row.id,
    name: row.name || '',
    artist: row.artist ?? null,
    commissioner: row.commissioner ?? null,
    amount: row.amount ?? 0,
    currency: row.currency || 'USD',
    description: row.description || ''
  }

  dialogVisible.value = true

  // Подтянуть референсы по id комиссии
  await loadReferences(row.id)
}

const buildFormData = () => {
  const fd = new FormData()

  fd.append('name', form.value.name || '')
  if (form.value.artist !== null && form.value.artist !== undefined) {
    fd.append('artist', form.value.artist)
  }
  if (form.value.commissioner !== null && form.value.commissioner !== undefined) {
    fd.append('commissioner', form.value.commissioner)
  }
  fd.append('amount', form.value.amount ?? 0)
  fd.append('currency', form.value.currency || 'USD')
  fd.append('description', form.value.description || '')

  // ---- Референсы ----
  const activeRefs = referenceImages.value.filter(r => !r.isDeleted)

  activeRefs.forEach((ref, idx) => {
    const prefix = `references[${idx}]`
    if (ref.id) {
      fd.append(`${prefix}[id]`, ref.id)
    }
    fd.append(`${prefix}[kind]`, ref.kind || 'ref')
    fd.append(`${prefix}[caption]`, ref.caption || '')
    fd.append(`${prefix}[source_url]`, ref.source_url || '')
    fd.append(`${prefix}[order]`, ref.order ?? idx)

    if (ref.file) {
      fd.append(`${prefix}[image]`, ref.file)
    }
  })

  // Удалённые существующие референсы — передаём id отдельным полем
  const deletedIds = referenceImages.value
      .filter(r => r.isDeleted && r.id)
      .map(r => r.id)

  deletedIds.forEach((id) => {
    fd.append('references_deleted[]', id)
  })

  return fd
}

const submitForm = async () => {
  saving.value = true
  try {
    const fd = buildFormData()

    if (isEdit.value && editingId.value) {
      await axios.patch(`/artworks/commissions/${editingId.value}/`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      ElMessage.success('Комиссия обновлена')
    } else {
      await axios.post('/artworks/commissions/', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      ElMessage.success('Комиссия создана')
    }

    dialogVisible.value = false
    await fetchCommissions()
  } catch (e) {
    console.error(e)
    ElMessage.error('Не удалось сохранить комиссию')
  } finally {
    saving.value = false
  }
}

const confirmDelete = (row) => {
  ElMessageBox.confirm(
      `Удалить комиссию #${row.id}?`,
      'Подтверждение',
      {
        type: 'warning',
        confirmButtonText: 'Удалить',
        cancelButtonText: 'Отмена'
      }
  ).then(() => deleteCommission(row.id))
}

const deleteCommission = async (id) => {
  try {
    await axios.delete(`/artworks/commissions/${id}/`)
    ElMessage.success('Комиссия удалена')
    await fetchCommissions()
  } catch (e) {
    console.error(e)
    ElMessage.error('Не удалось удалить комиссию')
  }
}
</script>

<style scoped>
.refs-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.refs-upload {
  margin-bottom: 8px;
}

.refs-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ref-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.ref-thumb {
  width: 96px;
  height: 96px;
  flex-shrink: 0;
  overflow: hidden;
  border-radius: 4px;
  background: #f5f5f5;
}

.ref-fields {
  flex: 1;
}

.ref-fields-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.ref-actions {
  margin-top: 4px;
  text-align: right;
}
</style>
