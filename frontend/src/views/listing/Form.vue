<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import api from '../../api'
import DynamicForm from '../../components/DynamicForm.vue'
import PhotoUploader from '../../components/PhotoUploader.vue'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => route.name === 'listing-edit')

const fields = ref([])
const form = ref({ title: '', share_url: '', notes: '' })
const photos = ref([])

onMounted(async () => {
  fields.value = await api.get('/api/field-template', {
    params: { target_type: 'listing' },
  })
  if (isEdit.value) {
    const data = await api.get(`/api/listing/${route.params.id}`)
    form.value = data
    photos.value = data.photos || []
  }
})

async function save() {
  if (isEdit.value) {
    await api.put(`/api/listing/${route.params.id}`, form.value)
    showSuccessToast('已保存')
    router.back()
  } else {
    const communityId = route.params.id
    await api.post('/api/listing', { ...form.value, community_id: communityId })
    showSuccessToast('已创建')
    router.push(`/community/${communityId}`)
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
      <van-field v-model="form.title" label="房源标题" placeholder="如：3号楼1502" />
      <van-field
        v-model="form.share_url"
        label="分享链接"
        placeholder="房产APP分享链接（回家后对比用）"
      />
    </van-cell-group>

    <DynamicForm v-model="form" :fields="fields" />

    <van-cell-group inset>
      <van-field v-model="form.notes" label="备注" type="textarea" autosize placeholder="房源特殊备注" />
    </van-cell-group>

    <div v-if="isEdit" class="photo-section">
      <div class="section-title">房屋照片</div>
      <PhotoUploader
        target-type="listing"
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
