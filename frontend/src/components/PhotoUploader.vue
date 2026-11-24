<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'
import api from '../api'
import { compressImage } from '../utils/image'

const props = defineProps({
  targetType: { type: String, required: true }, // community / listing
  targetId: { type: String, required: true },
  photos: { type: Array, default: () => [] }, // 已上传照片 [{id,url,caption}]
})
const emit = defineEmits(['uploaded', 'remove'])

const fileList = ref(
  props.photos.map((p) => ({ url: p.url, status: 'done', photoId: p.id }))
)

// 串行队列：多选时逐张上传，避免并发占满带宽导致超时报错
let uploadChain = Promise.resolve()

function onAfterRead(item) {
  item.status = 'uploading'
  item.message = '等待上传...'
  uploadChain = uploadChain
    .then(() => doUpload(item))
    .catch(() => {})
}

async function doUpload(item) {
  item.message = '压缩中...'
  try {
    const file = await compressImage(item.file)
    const formData = new FormData()
    formData.append('file', file, file.name || 'photo.jpg')
    formData.append('target_type', props.targetType)
    formData.append('target_id', props.targetId)
    item.message = '上传中...'
    const res = await api.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    item.status = 'done'
    item.message = ''
    item.url = res.url
    item.photoId = res.id
    emit('uploaded', res)
  } catch (e) {
    item.status = 'failed'
    item.message = '上传失败'
    showToast(e.message)
  }
}

function onDelete(item) {
  if (item.photoId) emit('remove', item.photoId)
}
</script>

<template>
  <div class="photo-uploader">
    <van-uploader
      v-model="fileList"
      multiple
      :max-count="20"
      :after-read="onAfterRead"
      :before-delete="() => true"
      @delete="onDelete"
    />
  </div>
</template>

<style scoped>
.photo-uploader {
  padding: 8px 0;
}
</style>
