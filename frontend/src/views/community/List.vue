<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api'

const router = useRouter()
const list = ref([])
const keyword = ref('')

const filtered = computed(() => {
  const kw = keyword.value.trim()
  if (!kw) return list.value
  return list.value.filter(
    (c) => (c.name || '').includes(kw) || (c.district || '').includes(kw)
  )
})

onMounted(load)

async function load() {
  try {
    list.value = await api.get('/api/community')
  } catch (e) {
    console.error(e)
  }
}
</script>

<template>
  <div>
    <van-search v-model="keyword" placeholder="搜索小区名称/区域" />

    <van-empty v-if="filtered.length === 0" description="暂无小区" />

    <van-cell-group inset v-for="c in filtered" :key="c.id" class="card">
      <van-cell is-link @click="router.push(`/community/${c.id}`)">
        <template #title>
          <div class="card-title">
            <span>{{ c.name }}</span>
            <van-tag v-if="c.score_avg != null" type="primary" round>
              {{ c.score_avg }} 分
            </van-tag>
          </div>
        </template>
        <template #label>
          <div class="card-label">
            <span v-if="c.district">{{ c.district }}</span>
          </div>
          <div class="card-meta">
            <span>📷 {{ c.photo_count || 0 }}</span>
            <span>🏠 {{ c.listing_count || 0 }} 套房源</span>
          </div>
        </template>
      </van-cell>
    </van-cell-group>

    <div class="fab">
      <van-button type="primary" round icon="plus" @click="router.push('/community/new')">
        添加小区
      </van-button>
    </div>
  </div>
</template>

<style scoped>
.card {
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-label {
  color: #969799;
  font-size: 13px;
  margin-top: 2px;
  display: flex;
  gap: 8px;
}
.card-meta {
  margin-top: 6px;
  color: #646566;
  font-size: 13px;
  display: flex;
  gap: 16px;
}
.fab {
  position: fixed;
  bottom: 80px;
  right: 20px;
}
</style>
