<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const items = [
  { title: '字段维护', desc: '小区/房源基本信息字段模板', path: '/admin/fields', icon: 'edit' },
  { title: '评分问题维护', desc: '评分的问题类别与选项', path: '/admin/questions', icon: 'star-o' },
  { title: '问答问题维护', desc: '看房问答的分类与问题', path: '/admin/qa', icon: 'chat-o' },
]
</script>

<template>
  <div>
    <div class="page-title">系统维护</div>
    <van-cell-group inset>
      <van-cell
        v-for="it in items"
        :key="it.path"
        :title="it.title"
        :label="it.desc"
        :icon="it.icon"
        is-link
        @click="router.push(it.path)"
      />
    </van-cell-group>
  </div>
</template>

<style scoped>
.page-title {
  font-size: 18px;
  font-weight: 700;
  margin: 8px 16px 16px;
}
</style>
