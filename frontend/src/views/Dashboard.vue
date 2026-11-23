<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const stats = ref({ communities: 0, listings: 0, scored: 0, photos: 0 })
const recent = ref([])

onMounted(async () => {
  try {
    const [communities, listings] = await Promise.all([
      api.get('/api/community'),
      api.get('/api/listing'),
    ])
    stats.value.communities = communities.length
    stats.value.listings = listings.length
    stats.value.scored = communities.filter((c) => c.score_avg != null).length
    stats.value.photos = communities.reduce((s, c) => s + (c.photo_count || 0), 0)
    recent.value = communities.slice(0, 5)
  } catch (e) {
    console.error(e)
  }
})

function go(path) {
  router.push(path)
}
</script>

<template>
  <div>
    <van-grid :column-num="2" :gutter="12" class="stat-grid">
      <van-grid-item>
        <div class="stat" @click="go('/community')">
          <div class="stat-num">{{ stats.communities }}</div>
          <div class="stat-label">小区</div>
        </div>
      </van-grid-item>
      <van-grid-item>
        <div class="stat">
          <div class="stat-num">{{ stats.listings }}</div>
          <div class="stat-label">房源</div>
        </div>
      </van-grid-item>
      <van-grid-item>
        <div class="stat">
          <div class="stat-num">{{ stats.scored }}</div>
          <div class="stat-label">已评分小区</div>
        </div>
      </van-grid-item>
      <van-grid-item>
        <div class="stat">
          <div class="stat-num">{{ stats.photos }}</div>
          <div class="stat-label">照片</div>
        </div>
      </van-grid-item>
    </van-grid>

    <div class="section">
      <div class="section-title">最近添加的小区</div>
      <van-empty v-if="recent.length === 0" description="还没有小区，去添加第一个吧" />
      <van-cell
        v-for="c in recent"
        :key="c.id"
        :title="c.name"
        :label="c.district || c.address || ''"
        is-link
        @click="go(`/community/${c.id}`)"
      >
        <template #value>
          <van-tag v-if="c.score_avg != null" type="primary">{{ c.score_avg }}分</van-tag>
        </template>
      </van-cell>
    </div>

    <div style="margin-top: 20px">
      <van-button type="primary" block icon="plus" @click="go('/community/new')">
        新建小区
      </van-button>
    </div>
  </div>
</template>

<style scoped>
.stat {
  text-align: center;
  padding: 8px 0;
}
.stat-num {
  font-size: 28px;
  font-weight: 700;
  color: #1989fa;
}
.stat-label {
  font-size: 13px;
  color: #969799;
  margin-top: 4px;
}
.section {
  margin-top: 20px;
}
.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  padding: 0 4px;
}
</style>
