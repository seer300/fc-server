<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import api from '../../api'
import DynamicForm from '../../components/DynamicForm.vue'
import PhotoUploader from '../../components/PhotoUploader.vue'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)

const fields = ref([])
const form = ref({ name: '', district: '', address: '', notes: '' })
const photos = ref([])

onMounted(async () => {
  fields.value = await api.get('/api/field-template', {
    params: { target_type: 'community' },
  })
  if (isEdit.value) {
    const data = await api.get(`/api/community/${route.params.id}`)
    form.value = data
    photos.value = data.photos || []
  }
})

async function save() {
  if (!form.value.name) {
    showToast('请填写小区名称')
    return
  }
  if (isEdit.value) {
    await api.put(`/api/community/${route.params.id}`, form.value)
    showSuccessToast('已保存')
    router.push(`/community/${route.params.id}`)
  } else {
    const res = await api.post('/api/community', form.value)
    showSuccessToast('已创建')
    router.push(`/community/${res.id}`)
  }
}

function onUploaded() {}
async function onRemove(photoId) {
  await api.delete(`/api/photo/${photoId}`)
}
</script>

<template>
  <div>
    <van-cell-group inset>
      <van-field v-model="form.name" label="小区名称" required placeholder="请输入小区名称" />
      <van-field v-model="form.district" label="区域" placeholder="如：浦东新区" />
    </van-cell-group>

    <DynamicForm v-model="form" :fields="fields" />

    <van-cell-group inset>
      <van-field
        v-model="form.notes"
        label="备注"
        type="textarea"
        autosize
        placeholder="特殊备注、中介联系方式等"
      />
    </van-cell-group>

    <div v-if="isEdit" class="photo-section">
      <div class="section-title">小区照片（含中介实拍）</div>
      <PhotoUploader
        target-type="community"
        :target-id="route.params.id"
        :photos="photos"
        @uploaded="onUploaded"
        @remove="onRemove"
      />
    </div>

    <div class="submit-bar">
      <van-button type="primary" block @click="save">保存</van-button>
    </div>
  </div>
</template>

<style scoped>
.photo-section {
  margin-top: 16px;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  margin: 8px 16px;
}
.submit-bar {
  margin: 20px 16px;
}
</style>
