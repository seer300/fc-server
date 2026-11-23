<script setup>
import { ref, onMounted, computed } from 'vue'
import { showConfirmDialog, showToast, showSuccessToast } from 'vant'
import api from '../../api'

const categories = ref([])
const questions = ref([])

const DEFAULT_OPTIONS_TEXT = '非常满意|5\n满意|4\n一般|3\n不满|2\n很差|1'

const showCat = ref(false)
const catEditId = ref(null)
const catForm = ref({})

const showQ = ref(false)
const qEditId = ref(null)
const qForm = ref({})
const qOptionsText = ref('')

onMounted(load)

async function load() {
  categories.value = await api.get('/api/question/categories')
  questions.value = await api.get('/api/question')
}

const questionsByCat = computed(() => {
  const map = {}
  categories.value.forEach((c) => (map[c.id] = []))
  questions.value.forEach((q) => {
    if (map[q.category_id]) map[q.category_id].push(q)
  })
  return map
})

// ---------- 类别 ----------
function openCatAdd() {
  catEditId.value = null
  catForm.value = { name: '', weight: 1.0, sort: categories.value.length + 1 }
  showCat.value = true
}
function openCatEdit(c) {
  catEditId.value = c.id
  catForm.value = { ...c }
  showCat.value = true
}
async function saveCat() {
  if (!catForm.value.name) {
    showToast('请输入类别名称')
    return
  }
  if (catEditId.value) await api.put(`/api/question/categories/${catEditId.value}`, catForm.value)
  else await api.post('/api/question/categories', catForm.value)
  showSuccessToast('已保存')
  showCat.value = false
  load()
}
async function delCat(c) {
  await showConfirmDialog({ title: '确认删除', message: `删除类别「${c.name}」及其问题？` })
  await api.delete(`/api/question/categories/${c.id}`)
  showSuccessToast('已删除')
  load()
}

// ---------- 问题 ----------
function openQAdd(catId) {
  qEditId.value = null
  qForm.value = { category_id: catId, question_text: '', question_type: 'single', options: [] }
  qOptionsText.value = DEFAULT_OPTIONS_TEXT
  showQ.value = true
}
function openQEdit(q) {
  qEditId.value = q.id
  qForm.value = { ...q }
  qOptionsText.value = (q.options || []).map((o) => `${o.text}|${o.score}`).join('\n')
  showQ.value = true
}
async function saveQ() {
  if (!qForm.value.question_text) {
    showToast('请输入问题')
    return
  }
  qForm.value.options = qOptionsText.value
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean)
    .map((line) => {
      const parts = line.split(/[|,，]/).map((x) => x.trim())
      return { text: parts[0], score: Number(parts[1]) || 0 }
    })
  if (qEditId.value) await api.put(`/api/question/${qEditId.value}`, qForm.value)
  else await api.post('/api/question', qForm.value)
  showSuccessToast('已保存')
  showQ.value = false
  load()
}
async function delQ(q) {
  await showConfirmDialog({ title: '确认删除', message: `删除问题「${q.question_text}」？` })
  await api.delete(`/api/question/${q.id}`)
  showSuccessToast('已删除')
  load()
}
</script>

<template>
  <div>
    <div v-for="c in categories" :key="c.id" class="cat-block">
      <div class="cat-header">
        <div class="cat-name">
          {{ c.name }}
          <van-tag type="primary" plain>权重 {{ c.weight }}</van-tag>
        </div>
        <div class="cat-actions">
          <van-button size="mini" icon="plus" @click="openQAdd(c.id)">问题</van-button>
          <van-button size="mini" @click="openCatEdit(c)">编辑</van-button>
          <van-button size="mini" type="danger" @click="delCat(c)">删除</van-button>
        </div>
      </div>
      <van-cell-group inset>
        <van-cell
          v-for="q in questionsByCat[c.id]"
          :key="q.id"
          :title="q.question_text"
        >
          <template #label>
            <span class="q-options">
              {{ (q.options || []).map((o) => o.text).join(' / ') }}
            </span>
          </template>
          <template #value>
            <van-button size="mini" @click="openQEdit(q)">编辑</van-button>
            <van-button size="mini" type="danger" @click="delQ(q)">删除</van-button>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <div class="add-bar">
      <van-button type="primary" round icon="plus" @click="openCatAdd">添加类别</van-button>
    </div>

    <!-- 类别弹窗 -->
    <van-popup v-model:show="showCat" position="bottom" round>
      <div class="popup-body">
        <div class="popup-title">{{ catEditId ? '编辑类别' : '添加类别' }}</div>
        <van-field v-model="catForm.name" label="类别名称" placeholder="如：地段交通" />
        <van-field v-model="catForm.weight" label="权重" type="number" placeholder="如：1.5" />
        <van-field v-model="catForm.sort" label="排序" type="number" />
        <div class="popup-actions">
          <van-button plain block @click="showCat = false">取消</van-button>
          <van-button type="primary" block @click="saveCat">保存</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 问题弹窗 -->
    <van-popup v-model:show="showQ" position="bottom" round :style="{ maxHeight: '85%' }">
      <div class="popup-body">
        <div class="popup-title">{{ qEditId ? '编辑问题' : '添加问题' }}</div>
        <van-field v-model="qForm.question_text" label="问题" placeholder="如：离地铁步行时间" />
        <van-field
          v-model="qOptionsText"
          label="选项"
          type="textarea"
          autosize
          placeholder="每行一个：选项文本|分数"
        />
        <van-field v-model="qForm.sort" label="排序" type="number" />
        <div class="popup-actions">
          <van-button plain block @click="showQ = false">取消</van-button>
          <van-button type="primary" block @click="saveQ">保存</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.cat-block {
  margin-bottom: 16px;
}
.cat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
}
.cat-name {
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
}
.cat-actions {
  display: flex;
  gap: 6px;
}
.q-options {
  color: #969799;
  font-size: 12px;
}
.add-bar {
  margin: 20px 0;
  text-align: center;
}
.popup-body {
  padding: 20px 16px;
}
.popup-title {
  font-size: 18px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 16px;
}
.popup-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}
</style>
