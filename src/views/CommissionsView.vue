<template>
  <div>
    <div style="display:flex; justify-content: space-between; margin-bottom: 16px;">
      <h2>Artworks</h2>
      <el-button type="primary" @click="openCreate">Создать работу</el-button>
    </div>

    <!-- Таблица -->
    <el-table
        :data="artworks"
        v-loading="loading"
        style="width: 100%;"
        size="small"
    >
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="type" label="Тип" width="140">
        <template #default="{ row }">
          {{ typeLabel(row.type) }}
        </template>
      </el-table-column>
      <el-table-column prop="purpose" label="Цель" width="140">
        <template #default="{ row }">
          {{ purposeLabel(row.purpose) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="Статус" width="140">
        <template #default="{ row }">
          {{ statusLabel(row.status) }}
        </template>
      </el-table-column>
      <el-table-column prop="date" label="Дата" width="140" />
      <el-table-column label="Финальный арт" width="120">
        <template #default="{ row }">
          <el-image
              v-if="row.final_image_url"
              :src="row.final_image_url"
              style="width:60px; height:60px; object-fit: cover; border-radius: 4px;"
              :preview-src-list="[row.final_image_url]"
          />
          <span v-else>-</span>
        </template>
      </el-table-column>

      <el-table-column label="Действия" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">Редактировать</el-button>
          <el-button
              size="small"
              type="danger"
              @click="confirmDelete(row)"
          >
            Удалить
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
        v-if="false"
        layout="prev, pager, next"
        :total="artworks.length"
        style="margin-top: 12px; text-align: right;"
    />

    <!-- Диалог создания / редактирования -->
    <el-dialog
        v-model="dialogVisible"
        :title="isEdit ? 'Редактировать работу' : 'Создать работу'"
        width="600px"
    >
      <el-form
          :model="form"
          label-position="top"
          :disabled="saving"
      >
        <el-form-item label="Описание">
          <el-input
              type="textarea"
              v-model="form.description"
              rows="3"
              clearable
          />
        </el-form-item>

        <el-form-item label="Тип">
          <el-select v-model="form.type" placeholder="Выберите тип">
            <el-option
                v-for="opt in TYPE_OPTIONS"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Цель">
          <el-select v-model="form.purpose" placeholder="Выберите цель">
            <el-option
                v-for="opt in PURPOSE_OPTIONS"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Статус">
          <el-select v-model="form.status" placeholder="Выберите статус">
            <el-option
                v-for="opt in STATUS_OPTIONS"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Ожидаемая дата завершения">
          <el-date-picker
              v-model="form.expected_completion_date"
              type="date"
              placeholder="Ожидаемая дата"
              style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="Фактическая дата завершения">
          <el-date-picker
              v-model="form.actual_completion_date"
              type="date"
              placeholder="Фактическая дата"
              style="width: 100%;"
          />
        </el-form-item>

        <!-- slot / commission можно завязать на другие селекты, пока просто id -->
        <el-form-item label="Slot ID">
          <el-input
              v-model.number="form.slot"
              placeholder="ID слота или оставьте пустым"
          />
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
                  v-for="(refImg, index) in referenceImages"
                  :key="refImg.uid || refImg.id || index"
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
                        @click="removeReference(index)"
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


        <el-form-item label="Commission ID">
          <el-input
              v-model.number="form.commission"
              placeholder="ID комиссии или оставьте пустым"
          />
        </el-form-item>

        <el-form-item label="Финальное изображение">
          <div style="display:flex; gap:12px; align-items:flex-start;">
            <div v-if="form.final_image_url && !newImageFile">
              <el-image
                  :src="form.final_image_url"
                  style="width:80px; height:80px; object-fit:cover; border-radius:4px;"
                  :preview-src-list="[form.final_image_url]"
              />
            </div>
            <el-upload
                class="upload-demo"
                :auto-upload="false"
                :show-file-list="true"
                :on-change="handleFileChange"
            >
              <el-button type="primary">Выбрать файл</el-button>
              <template #tip>
                <div style="font-size: 12px; color: #999;">
                  Поддерживаются: jpg, jpeg, png, webp
                </div>
              </template>
            </el-upload>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false" :disabled="saving">
          Отмена
        </el-button>
        <el-button
            type="primary"
            @click="submitForm"
            :loading="saving"
        >
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
import { Plus } from '@element-plus/icons-vue'


const artworks = ref([])
const loading = ref(false)
const saving = ref(false)

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const newImageFile = ref(null)


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

const TYPE_OPTIONS = [
  { value: 'lineart', label: 'Лайнарт' },
  { value: 'flat_colors', label: 'Плоские цвета' },
  { value: 'sketch', label: 'Скетч' },
  { value: 'basic_render', label: 'Базовый рендер' },
  { value: 'premium_render', label: 'Премиальный рендер' }
]

const PURPOSE_OPTIONS = [
  { value: 'commission', label: 'Заказ' },
  { value: 'promo', label: 'Промоматериалы' },
  { value: 'collab', label: 'Коллаборация' }
]

const STATUS_OPTIONS = [
  { value: 'pending', label: 'Pending' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' }
]

const emptyForm = () => ({
  id: null,
  description: '',
  type: 'lineart',
  purpose: 'commission',
  slot: null,
  date: null,
  status: 'pending',
  commission: null,
  expected_completion_date: null,
  actual_completion_date: null,
  final_image_url: null
})

const form = ref(emptyForm())

const typeLabel = (value) =>
    TYPE_OPTIONS.find(o => o.value === value)?.label || value

const purposeLabel = (value) =>
    PURPOSE_OPTIONS.find(o => o.value === value)?.label || value

const statusLabel = (value) =>
    STATUS_OPTIONS.find(o => o.value === value)?.label || value

const fetchArtworks = async () => {
  loading.value = true
  try {
    const { data } = await axios.get('/artworks/artworks')
    artworks.value = data
  } catch (err) {
    console.error(err)
    ElMessage.error('Не удалось загрузить список работ')
  } finally {
    loading.value = false
  }
}

onMounted(fetchArtworks)

const handleRefFilesChange = (file, fileList) => {
  // file – последний добавленный файл
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

const removeReference = (index) => {
  const item = referenceImages.value[index]
  if (!item) return

  // Если уже существует на сервере — помечаем как удалённый, чтобы передать id
  if (item.id && !item.isNew) {
    item.isDeleted = true
  } else {
    // Новый, ещё не сохранённый — просто убираем из списка
    referenceImages.value.splice(index, 1)
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

const openCreate = () => {
  isEdit.value = false
  editingId.value = null
  form.value = emptyForm()
  newImageFile.value = null
  referenceImages.value = []      // <--- сбросить
  dialogVisible.value = true
}

const openEdit = async (row) => {
  isEdit.value = true
  editingId.value = row.id
  form.value = {
    id: row.id,
    description: row.description,
    type: row.type,
    purpose: row.purpose,
    slot: row.slot,
    status: row.status,
    commission: row.commission,
    expected_completion_date: row.expected_completion_date,
    actual_completion_date: row.actual_completion_date,
    final_image_url: row.final_image_url
  }
  newImageFile.value = null

  dialogVisible.value = true

  // Подтянуть референсы по commission
  if (row.commission) {
    await loadReferences(row.commission)
  } else {
    referenceImages.value = []
  }
}


const handleFileChange = (file) => {
  newImageFile.value = file.raw
}
const buildFormData = () => {
  const fd = new FormData()

  fd.append('description', form.value.description || '')
  fd.append('type', form.value.type || 'lineart')
  fd.append('purpose', form.value.purpose || 'commission')
  fd.append('status', form.value.status || 'pending')

  if (form.value.date) {
    fd.append('date', formatDate(form.value.date))
  }
  if (form.value.expected_completion_date) {
    fd.append('expected_completion_date', formatDate(form.value.expected_completion_date))
  }
  if (form.value.actual_completion_date) {
    fd.append('actual_completion_date', formatDate(form.value.actual_completion_date))
  }

  fd.append('slot', form.value.slot || '')
  fd.append('commission', form.value.commission || '')

  if (newImageFile.value) {
    fd.append('final_image', newImageFile.value)
  }

  // ---- Референсы ----
  // Неудалённые элементы -> отправляем как references[index][...]
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


const formatDate = (val) => {
  if (!val) return ''
  // Element Plus может отдавать Date или строку
  const d = val instanceof Date ? val : new Date(val)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const submitForm = async () => {
  saving.value = true
  try {
    const fd = buildFormData()

    let response
    if (isEdit.value && editingId.value) {
      response = await axios.patch(`/artworks/${editingId.value}/`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      ElMessage.success('Работа обновлена')
    } else {
      response = await axios.post('/artworks/artworks', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      ElMessage.success('Работа создана')
    }

    dialogVisible.value = false
    await fetchArtworks()
    return response
  } catch (err) {
    console.error(err)
    ElMessage.error('Не удалось сохранить работу')
  } finally {
    saving.value = false
  }
}

const confirmDelete = (row) => {
  ElMessageBox.confirm(
      `Удалить работу #${row.id}?`,
      'Подтверждение',
      {
        type: 'warning',
        confirmButtonText: 'Удалить',
        cancelButtonText: 'Отмена'
      }
  ).then(() => deleteArtwork(row.id))
}

const deleteArtwork = async (id) => {
  try {
    await axios.delete(`/artworks/artworks/${id}/`)
    ElMessage.success('Работа удалена')
    await fetchArtworks()
  } catch (err) {
    console.error(err)
    ElMessage.error('Не удалось удалить работу')
  }
}
</script>

<style scoped>
.upload-demo {
  margin-top: 4px;
}
</style>
