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
  'id', 'title', 'share_url', 'community_id', 'notes',
  'created_at', 'updated_at', 'photos', 'photo_count',
]

onMounted(load)

async function load() {
  const [data, fields] = await Promise.all([
    api.get(`/api/listing/${route.params.id}`),
    api.get('/api/field-template', { params: { target_type: 'listing' } }),
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

function goQa() {
  router.push(`/listing/${route.params.id}/qa`)
}
function goEdit() {
  router.push(`/listing/${route.params.id}/edit`)
}
function goCommunity() {
  if (detail.value?.community_id) router.push(`/community/${detail.value.community_id}`)
}

// ---------- 长按/点击复制分享链接 ----------
let pressTimer = null
let longPressed = false

async function copyShareUrl() {
  const text = detail.value?.share_url
  if (!text) return
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
    } else {
      const ta = document.createElement('textarea')
      ta.value = text
      ta.style.position = 'fixed'
      ta.style.opacity = '0'
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
    showToast('链接已复制')
  } catch (e) {
    showToast('复制失败，请手动复制')
  }
}

function onPressStart() {
  longPressed = false
  clearTimeout(pressTimer)
  pressTimer = setTimeout(() => {
    longPressed = true
    copyShareUrl()
  }, 600)
}
function onPressEnd() {
  clearTimeout(pressTimer)
}
function onCellClick() {
  if (!longPressed) copyShareUrl()
  longPressed = false
}
async function del() {
  await showConfirmDialog({ title: '确认删除', message: '删除该房源及其照片？' })
  await api.delete(`/api/listing/${route.params.id}`)
  showToast('已删除')
  router.back()
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
    <van-nav-bar :title="detail.title || '房源'" left-arrow @click-left="router.back()" fixed placeholder />

    <!-- 分享链接 -->
    <van-cell-group inset v-if="detail.share_url">
      <van-cell
        title="APP分享链接"
        clickable
        @pointerdown="onPressStart"
        @pointerup="onPressEnd"
        @pointerleave="onPressEnd"
        @pointercancel="onPressEnd"
        @click="onCellClick"
      >
        <template #label>
          <span class="share-url">{{ detail.share_url }}</span>
        </template>
        <template #value>
          <span class="copy-hint">长按/点击复制</span>
        </template>
      </van-cell>
    </van-cell-group>

    <!-- 动态字段 -->
    <van-cell-group v-if="dynamicEntries.length" inset title="基本信息">
      <van-cell v-for="[k, v] in dynamicEntries" :key="k" :title="labelMap[k] || k" :value="String(v)" />
    </van-cell-group>

    <!-- 照片 -->
    <div class="section">
      <div class="section-title">房屋照片</div>
      <van-swipe v-if="photos.length" :autoplay="3000" lazy-render class="swipe">
        <van-swipe-item v-for="p in photos" :key="p.id">
          <img :src="p.url" class="photo" />
          <div v-if="p.caption" class="caption">{{ p.caption }}</div>
        </van-swipe-item>
      </van-swipe>
      <PhotoUploader
        target-type="listing"
        :target-id="detail.id"
        :photos="photos"
        @uploaded="onUploaded"
        @remove="onRemove"
      />
    </div>

    <!-- 备注 -->
    <div v-if="detail.notes" class="section">
      <div class="section-title">备注</div>
      <div class="notes-content">{{ detail.notes }}</div>
    </div>

    <!-- 操作 -->
    <div class="actions">
      <van-button type="primary" block icon="records" @click="goQa">看房问答</van-button>
      <van-button plain type="primary" block @click="goEdit">编辑</van-button>
      <van-button plain block @click="goCommunity">所属小区</van-button>
      <van-button type="danger" block @click="del">删除</van-button>
    </div>
  </div>
</template>

<style scoped>
.share-url {
  color: #1989fa;
  font-size: 12px;
}
.copy-hint {
  color: #969799;
  font-size: 12px;
}
.section {
  margin-top: 16px;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  margin: 8px 16px;
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
