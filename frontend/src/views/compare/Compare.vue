<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

const communities = ref([])
const selectedIds = ref([])
const fields = ref([])

const FIXED = [
  'id', 'name', 'photos', 'listings', 'created_at', 'updated_at',
  'score_detail', 'photo_count', 'listing_count', 'score_avg',
]

onMounted(async () => {
  communities.value = await api.get('/api/community')
  fields.value = await api.get('/api/field-template', {
    params: { target_type: 'community' },
  })
})

const selected = computed(() =>
  communities.value.filter((c) => selectedIds.value.includes(c.id))
)

const labelMap = computed(() => {
  const m = { district: '区域', address: '地址' }
  fields.value.forEach((f) => (m[f.field_key] = f.field_label))
  return m
})

const allKeys = computed(() => {
  const keys = new Set(['district', 'address'])
  fields.value.forEach((f) => keys.add(f.field_key))
  selected.value.forEach((c) =>
    Object.keys(c).forEach((k) => {
      if (!FIXED.includes(k)) keys.add(k)
    })
  )
  return [...keys]
})

function toggle(id) {
  const i = selectedIds.value.indexOf(id)
  if (i >= 0) selectedIds.value.splice(i, 1)
  else selectedIds.value.push(id)
}
</script>

<template>
  <div>
    <van-cell-group inset title="选择要对比的小区（可多选）">
      <van-checkbox-group v-model="selectedIds">
        <van-cell
          v-for="c in communities"
          :key="c.id"
          clickable
          :title="c.name"
          @click="toggle(c.id)"
        >
          <template #right-icon>
            <van-checkbox :name="c.id" @click.stop />
          </template>
        </van-cell>
      </van-checkbox-group>
    </van-cell-group>

    <div v-if="selected.length" class="table-wrap">
      <table class="compare-table">
        <thead>
          <tr>
            <th>维度</th>
            <th v-for="c in selected" :key="c.id">{{ c.name }}</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>综合评分</td>
            <td v-for="c in selected" :key="c.id">
              <strong>{{ c.score_avg ?? '-' }}</strong>
            </td>
          </tr>
          <tr v-for="k in allKeys" :key="k">
            <td>{{ labelMap[k] || k }}</td>
            <td v-for="c in selected" :key="c.id">{{ c[k] ?? '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <van-empty v-else description="选择 2 个以上小区开始对比" />
  </div>
</template>

<style scoped>
.table-wrap {
  margin-top: 16px;
  overflow-x: auto;
  background: #fff;
  border-radius: 8px;
}
.compare-table {
  border-collapse: collapse;
  min-width: 100%;
}
.compare-table th,
.compare-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #ebedf0;
  font-size: 13px;
  white-space: nowrap;
}
.compare-table th {
  background: #f7f8fa;
  font-weight: 600;
}
.compare-table td:first-child {
  font-weight: 600;
  color: #646566;
  background: #fafafa;
}
</style>
