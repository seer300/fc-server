import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '首页' } },
  { path: '/community', name: 'community-list', component: () => import('../views/community/List.vue'), meta: { title: '小区' } },
  { path: '/community/new', name: 'community-new', component: () => import('../views/community/Form.vue'), meta: { title: '新建小区' } },
  { path: '/community/:id', name: 'community-detail', component: () => import('../views/community/Detail.vue'), meta: { title: '小区详情' } },
  { path: '/community/:id/edit', name: 'community-edit', component: () => import('../views/community/Form.vue'), meta: { title: '编辑小区' } },
  { path: '/community/:id/score', name: 'community-score', component: () => import('../views/score/ScoreForm.vue'), meta: { title: '评分' } },
  { path: '/community/:id/qa', name: 'community-qa', component: () => import('../views/qa/QaForm.vue'), meta: { title: '小区问答' } },
  { path: '/community/:id/listing/new', name: 'listing-new', component: () => import('../views/listing/Form.vue'), meta: { title: '新增房源' } },
  { path: '/listing/:id', name: 'listing-detail', component: () => import('../views/listing/Detail.vue'), meta: { title: '房源详情' } },
  { path: '/listing/:id/edit', name: 'listing-edit', component: () => import('../views/listing/Form.vue'), meta: { title: '编辑房源' } },
  { path: '/listing/:id/qa', name: 'listing-qa', component: () => import('../views/qa/QaForm.vue'), meta: { title: '房源问答' } },
  { path: '/compare', name: 'compare', component: () => import('../views/compare/Compare.vue'), meta: { title: '横向对比' } },
  { path: '/admin', name: 'admin-home', component: () => import('../views/admin/AdminHome.vue'), meta: { title: '维护' } },
  { path: '/admin/fields', name: 'admin-fields', component: () => import('../views/admin/FieldAdmin.vue'), meta: { title: '字段维护' } },
  { path: '/admin/questions', name: 'admin-questions', component: () => import('../views/admin/QuestionAdmin.vue'), meta: { title: '评分问题维护' } },
  { path: '/admin/qa', name: 'admin-qa', component: () => import('../views/admin/QaAdmin.vue'), meta: { title: '问答问题维护' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
