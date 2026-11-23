<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import api from '../../api'

const route = useRoute()
const router = useRouter()

const targetType = computed(() => (route.path.includes('/listing/') ? 'listing' : 'community'))
const targetId = computed(() => route.params.id)

const categories = ref([])
const questions = ref([])
const activeCategoryId = ref(null)

// question_id -> { option, note, photo }
const answers = reactive({})
// question_id -> van-uploader 的 fileList
const fileLists = reactive({})

const answerPicker = ref({ show: false, qid: null, columns: [] })
const showCategory = ref(false)

onMounted(load)

async function load() {
  categories.value = await api.get('/api/qa/categories', {
    params: { target_type: targetType.value },
  })
  questions.value = await api.get('/api/qa/questions', {
    params: { target_type: targetType.value },
  })

  // 初始化每行的答案与文件列表
  questions.value.forEach((q) => {
    if (!answers[q.id]) answers[q.id] = { option: null, note: '', photo: null }
    if (!fileLists[q.id]) fileLists[q.id] = []
  })

  // 回显已保存答案
  const records = await api.get(`/api/qa/answers/${targetType.value}/${targetId.value}`)
  records.forEach((r) => {
    answers[r.question_id] = { option: r.option, note: r.note || '', photo: r.photo || null }
    if (r.photo) fileLists[r.question_id] = [{ url: r.photo.url, status: 'done' }]
  })

  if (categories.value.length) activeCategoryId.value = categories.value[0].id
}

const currentQuestions = computed(() =>
  questions.value.filter((q) => q.category_id === activeCategoryId.value)
)

// ---------- 答案下拉 ----------
function openAnswerPicker(q) {
  answerPicker.value = {
    show: true,
    qid: q.id,
    columns: (q.options || []).map((o) => ({ text: o.label, value: o.value })),
  }
}

function onAnswerConfirm({ selectedOptions }) {
  const val = selectedOptions[0]?.value
  const label = selectedOptions[0]?.text
  if (answerPicker.value.qid) {
    answers[answerPicker.value.qid].option = { label, value: val }
  }
  answerPicker.value.show = false
}

// ---------- 照片上传（单张） ----------
async function afterRead(qid, item) {
  item.status = 'uploading'
  item.message = '上传中...'
  try {
    const formData = new FormData()
    formData.append('file', item.file)
    formData.append('target_type', targetType.value)
    formData.append('target_id', targetId.value)
    formData.append('save_record', 'false')
    const res = await api.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    item.url = res.url
    item.status = 'done'
    item.message = ''
    answers[qid].photo = { url: res.url, thumb_url: res.thumb_url, file_key: res.file_key }
  } catch (e) {
    item.status = 'failed'
    item.message = '上传失败'
    showToast(e.message)
  }
}

function removePhoto(qid) {
  answers[qid].photo = null
  fileLists[qid] = []
}

// ---------- 提交 ----------
async function submit() {
  const payload = questions.value
    .filter((q) => {
      const a = answers[q.id]
      return a && (a.option || a.note || a.photo)
    })
    .map((q) => ({
      question_id: q.id,
      option: answers[q.id].option,
      note: answers[q.id].note,
      photo: answers[q.id].photo,
    }))

  if (payload.length === 0) {
    showToast('请至少填写一项')
    return
  }
  await api.post(`/api/qa/answers/${targetType.value}/${targetId.value}`, payload)
  showSuccessToast('已保存')
  router.back()
}
</script>

<template>
  <div>
    <!-- 分类下拉 -->
    <van-cell-group inset>
      <van-field
        :model-value="categories.find((c) => c.id === activeCategoryId)?.name"
        label="问题类型"
        readonly
        is-link
        placeholder="请选择分类"
        @click="showCategory = true"
      />
    </van-cell-group>

    <van-empty v-if="currentQuestions.length === 0" description="该分类下暂无问题" />

    <!-- 问题列表 -->
    <div v-for="q in currentQuestions" :key="q.id" class="q-card">
      <div class="q-text">{{ q.question_text }}</div>

      <div class="q-row">
        <van-field
          :model-value="answers[q.id]?.option?.label"
          readonly
          is-link
          placeholder="选择答案"
          class="answer-field"
          @click="openAnswerPicker(q)"
        />
        <van-uploader
          v-model="fileLists[q.id]"
          :max-count="1"
          :after-read="(item) => afterRead(q.id, item)"
        />
      </div>

      <van-field
        v-model="answers[q.id].note"
        type="textarea"
        autosize
        rows="1"
        placeholder="备注（可选）"
      />

      <div v-if="answers[q.id]?.photo" class="photo-preview">
        <img :src="answers[q.id].photo.thumb_url || answers[q.id].photo.url" />
        <van-icon name="clear" class="remove" @click="removePhoto(q.id)" />
      </div>
    </div>

    <div class="submit-bar">
      <van-button type="primary" block @click="submit">保存当前进度</van-button>
    </div>

    <!-- 分类选择 -->
    <van-popup v-model:show="showCategory" position="bottom" round>
      <van-picker
        :columns="categories.map((c) => ({ text: c.name, value: c.id }))"
        @confirm="({ selectedOptions }) => { activeCategoryId = selectedOptions[0].value; showCategory = false }"
        @cancel="showCategory = false"
      />
    </van-popup>

    <!-- 答案选择 -->
    <van-popup v-model:show="answerPicker.show" position="bottom" round>
      <van-picker
        :columns="answerPicker.columns"
        @confirm="onAnswerConfirm"
        @cancel="answerPicker.show = false"
      />
    </van-popup>
  </div>
</template>

<style scoped>
.q-card {
  background: #fff;
  border-radius: 8px;
  margin: 12px 16px;
  padding: 12px;
}
.q-text {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
}
.q-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.answer-field {
  flex: 1;
}
.photo-preview {
  position: relative;
  display: inline-block;
  margin-top: 8px;
}
.photo-preview img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
}
.remove {
  position: absolute;
  top: -8px;
  right: -8px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  border-radius: 50%;
}
.submit-bar {
  margin: 20px 16px;
}
</style>
