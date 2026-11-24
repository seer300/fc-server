<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import api from '../../api'
import PhotoUploader from '../../components/PhotoUploader.vue'

const route = useRoute()
const router = useRouter()
const detail = ref(null)
const labelMap = ref({})

const FIXED_KEYS = [
  'id', 'name', 'district', 'address', 'notes', 'created_at', 'updated_at',
  'score_avg', 'score_detail', 'photos', 'listings', 'photo_count', 'listing_count',
]

onMounted(load)

async function load() {
  const [data, fields] = await Promise.all([
    api.get(`/api/community/${route.params.id}`),
    api.get('/api/field-template', { params: { target_type: 'community' } }),
  ])
  detail.value = data
  fields.forEach((f) => (labelMap.value[f.field_key] = f.field_label))
}

const dynamicEntries = computed(() => {
  if (!detail.value) return []
  return Object.entries(detail.value).filter(
    ([k, v]) => !FIXED_KEYS.includes(k) && v != null && v !== ''
  )
})

const photos = computed(() => detail.value?.photos || [])

function goScore() {
  router.push(`/community/${route.params.id}/score`)
}
function goQa() {
  router.push(`/community/${route.params.id}/qa`)
}
function goNewListing() {
  router.push(`/community/${route.params.id}/listing/new`)
}
function goEdit() {
  router.push(`/community/${route.params.id}/edit`)
}
async function del() {
  await showConfirmDialog({
    title: '确认删除',
    message: '删除小区将同时删除其房源和照片',
  })
  await api.delete(`/api/community/${route.params.id}`)
  showToast('已删除')
  router.push('/community')
}
async function onUploaded() {
  await load()
}
async function onRemove(photoId) {
  await api.delete(`/api/photo/${photoId}`)
  await load()
}
</script>

<template>
  <div v-if="detail">
    <van-nav-bar
      :title="detail.name"
      left-arrow
      @click-left="router.back()"
      fixed
      placeholder
    />

    <!-- 评分卡片 -->
    <van-cell-group inset v-if="detail.score_avg != null">
      <van-cell title="综合评分" :value="`${detail.score_avg} 分`" />
      <van-cell v-for="(s, k) in detail.score_detail || {}" :key="k" :title="k" :value="`${s} 分`" />
    </van-cell-group>
    <van-cell-group inset v-else>
      <van-cell title="综合评分" value="未评分" is-link @click="goScore" />
    </van-cell-group>

    <!-- 基本信息（固定字段） -->
    <van-cell-group inset title="基本信息">
      <van-cell title="区域" :value="detail.district || '-'" />
    </van-cell-group>

    <!-- 动态字段 -->
    <van-cell-group v-if="dynamicEntries.length" inset title="详细信息">
      <van-cell
        v-for="[k, v] in dynamicEntries"
        :key="k"
        :title="labelMap[k] || k"
        :value="String(v)"
      />
    </van-cell-group>

    <!-- 照片 -->
    <div class="section">
      <div class="section-title">小区照片</div>
      <van-swipe v-if="photos.length" :autoplay="3000" lazy-render class="swipe">
        <van-swipe-item v-for="p in photos" :key="p.id">
          <img :src="p.url" class="photo" />
          <div v-if="p.caption" class="caption">{{ p.caption }}</div>
        </van-swipe-item>
      </van-swipe>
      <PhotoUploader
        target-type="community"
        :target-id="detail.id"
        :photos="photos"
        @uploaded="onUploaded"
        @remove="onRemove"
      />
    </div>

    <!-- 房源列表 -->
    <div class="section">
      <div class="section-title">
        房源（{{ detail.listings?.length || 0 }}）
        <van-button size="mini" type="primary" icon="plus" @click="goNewListing">
          添加房源
        </van-button>
      </div>
      <van-empty v-if="!detail.listings?.length" description="暂无房源" />
      <van-cell
        v-for="l in detail.listings"
        :key="l.id"
        :title="l.title || '房源'"
        :label="`${l.price ?? ''} ${l.area ?? ''}`"
        is-link
        @click="router.push(`/listing/${l.id}`)"
      />
    </div>

    <!-- 备注 -->
    <div v-if="detail.notes" class="section">
      <div class="section-title">备注</div>
      <div class="notes-content">{{ detail.notes }}</div>
    </div>

    <!-- 操作 -->
    <div class="actions">
      <van-button type="primary" block @click="goScore">评分</van-button>
      <van-button type="primary" block icon="records" @click="goQa">看房问答</van-button>
      <van-button plain type="primary" block @click="goEdit">编辑</van-button>
      <van-button type="danger" block @click="del">删除</van-button>
    </div>
  </div>
</template>

<style scoped>
.section {
  margin-top: 16px;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  margin: 8px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.swipe {
  border-radius: 8px;
  overflow: hidden;
}
.photo {
  width: 100%;
  height: 220px;
  object-fit: cover;
  display: block;
}
.notes-content {
  margin: 0 16px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 8px;
  color: #323233;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
.caption {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px;
  background: rgba(0, 0, 0, 0.4);
  color: #fff;
  font-size: 13px;
}
.actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 20px 16px;
}
</style>
