<script setup>
import { ref, onMounted } from 'vue'
import { showConfirmDialog, showToast, showSuccessToast } from 'vant'
import api from '../../api'

const targetType = ref('community')
const fields = ref([])
const showForm = ref(false)
const showType = ref(false)
const editId = ref(null)
const form = ref({})
const optionsText = ref('')

const TYPE_OPTIONS = [
  { text: '文本', value: 'text' },
  { text: '数字', value: 'number' },
  { text: '下拉选择', value: 'select' },
  { text: '日期', value: 'date' },
  { text: '多行文本', value: 'textarea' },
]

onMounted(load)

async function load() {
  fields.value = await api.get('/api/field-template', {
    params: { target_type: targetType.value },
  })
}

function onTabChange() {
  load()
}

function openAdd() {
  editId.value = null
  form.value = {
    target_type: targetType.value,
    field_key: '',
    field_label: '',
    field_type: 'text',
    options: [],
    sort: fields.value.length + 1,
    required: false,
  }
  optionsText.value = ''
  showForm.value = true
}

function openEdit(f) {
  editId.value = f.id
  form.value = { ...f, options: f.options || [] }
  optionsText.value = (f.options || []).map((o) => o.label ?? o.value).join('\n')
  showForm.value = true
}

function onTypeConfirm({ selectedOptions }) {
  form.value.field_type = selectedOptions[0].value
  showType.value = false
}

async function save() {
  if (!form.value.field_key || !form.value.field_label) {
    showToast('请填写字段标识和字段名称')
    return
  }
  if (form.value.field_type === 'select') {
    form.value.options = optionsText.value
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean)
      .map((s) => ({ label: s, value: s }))
  }
  if (editId.value) {
    await api.put(`/api/field-template/${editId.value}`, form.value)
  } else {
    await api.post('/api/field-template', form.value)
  }
  showSuccessToast('已保存')
  showForm.value = false
  load()
}

async function del(f) {
  await showConfirmDialog({ title: '确认删除', message: `删除字段「${f.field_label}」？` })
  await api.delete(`/api/field-template/${f.id}`)
  showSuccessToast('已删除')
  load()
}
</script>

<template>
  <div>
    <van-tabs v-model:active="targetType" @change="onTabChange">
      <van-tab title="小区字段" name="community" />
      <van-tab title="房源字段" name="listing" />
    </van-tabs>

    <van-cell-group inset v-for="f in fields" :key="f.id" class="item">
      <van-cell>
        <template #title>
          <div class="field-title">
            {{ f.field_label }}
            <van-tag type="primary" plain>{{ f.field_type }}</van-tag>
            <van-tag v-if="f.required" type="danger" plain>必填</van-tag>
          </div>
        </template>
        <template #label>
          <div class="field-key">标识：{{ f.field_key }}</div>
        </template>
        <template #value>
          <van-button size="mini" @click="openEdit(f)">编辑</van-button>
          <van-button size="mini" type="danger" @click="del(f)">删除</van-button>
        </template>
      </van-cell>
    </van-cell-group>

    <div class="add-bar">
      <van-button type="primary" round icon="plus" @click="openAdd">添加字段</van-button>
    </div>

    <!-- 字段编辑弹窗 -->
    <van-popup v-model:show="showForm" position="bottom" round :style="{ maxHeight: '85%' }">
      <div class="popup-body">
        <div class="popup-title">{{ editId ? '编辑字段' : '添加字段' }}</div>
        <van-field v-model="form.field_label" label="字段名称" placeholder="如：绿化率" />
        <van-field v-model="form.field_key" label="字段标识" placeholder="如：greening_rate" />
        <van-field
          v-model="form.field_type"
          label="字段类型"
          readonly
          is-link
          @click="showType = true"
        />
        <van-field v-model="form.sort" label="排序" type="number" />
        <van-field label="是否必填">
          <template #input>
            <van-switch v-model="form.required" size="20" />
          </template>
        </van-field>
        <van-field
          v-if="form.field_type === 'select'"
          v-model="optionsText"
          label="选项"
          type="textarea"
          autosize
          placeholder="每行一个选项"
        />
        <div class="popup-actions">
          <van-button plain block @click="showForm = false">取消</van-button>
          <van-button type="primary" block @click="save">保存</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 类型选择 -->
    <van-popup v-model:show="showType" position="bottom" round>
      <van-picker :columns="TYPE_OPTIONS" @confirm="onTypeConfirm" @cancel="showType = false" />
    </van-popup>
  </div>
</template>

<style scoped>
.item {
  margin-bottom: 8px;
}
.field-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}
.field-key {
  color: #969799;
  font-size: 12px;
  margin-top: 4px;
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
