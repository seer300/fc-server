<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showSuccessToast } from 'vant'
import api from '../../api'

const route = useRoute()
const router = useRouter()
const categories = ref([])
const questions = ref([])
const answers = ref({}) // question_id -> {text, score}

onMounted(async () => {
  categories.value = await api.get('/api/question/categories')
  questions.value = await api.get('/api/question')
  const records = await api.get(`/api/score/${route.params.id}`)
  records.forEach((r) => (answers.value[r.question_id] = r.option))
})

const grouped = computed(() => {
  const map = {}
  categories.value.forEach((c) => (map[c.id] = { category: c, questions: [] }))
  questions.value.forEach((q) => {
    if (map[q.category_id]) map[q.category_id].questions.push(q)
  })
  return Object.values(map)
})

function selectOption(q, opt) {
  answers.value[q.id] = opt
}

async function submit() {
  const payload = Object.entries(answers.value).map(([question_id, option]) => ({
    question_id,
    option,
  }))
  await api.post(`/api/score/${route.params.id}`, payload)
  showSuccessToast('评分已保存')
  router.back()
}
</script>

<template>
  <div>
    <div v-for="g in grouped" :key="g.category.id" class="cat-block">
      <div class="cat-title">{{ g.category.name }}</div>
      <div v-for="q in g.questions" :key="q.id" class="q-block">
        <div class="q-text">{{ q.question_text }}</div>
        <div class="options">
          <van-button
            v-for="opt in q.options"
            :key="opt.text + '-' + opt.score"
            :type="answers[q.id]?.score === opt.score ? 'primary' : 'default'"
            size="small"
            round
            @click="selectOption(q, opt)"
          >
            {{ opt.text }}（{{ opt.score }}）
          </van-button>
        </div>
      </div>
    </div>

    <div class="submit-bar">
      <van-button type="primary" block @click="submit">保存评分</van-button>
    </div>
  </div>
</template>

<style scoped>
.cat-block {
  margin-bottom: 16px;
}
.cat-title {
  font-size: 16px;
  font-weight: 700;
  padding: 8px 16px;
  color: #1989fa;
}
.q-block {
  background: #fff;
  border-radius: 8px;
  margin: 8px 16px;
  padding: 12px;
}
.q-text {
  font-size: 14px;
  margin-bottom: 10px;
}
.options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.submit-bar {
  margin: 20px 16px;
}
</style>
