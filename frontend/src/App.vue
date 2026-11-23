<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isMobile = ref(window.innerWidth < 768)

const menus = [
  { path: '/', title: '首页', icon: 'wap-home-o' },
  { path: '/community', title: '小区', icon: 'location-o' },
  { path: '/compare', title: '对比', icon: 'chart-trending-o' },
  { path: '/admin', title: '维护', icon: 'setting-o' },
]

const currentTitle = computed(() => route.meta?.title || '房产管理系统')

function onResize() {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => window.addEventListener('resize', onResize))
onBeforeUnmount(() => window.removeEventListener('resize', onResize))
</script>

<template>
  <div class="app-shell">
    <!-- 桌面端侧边栏 -->
    <aside v-if="!isMobile" class="sidebar">
      <div class="logo">🏠 房产管理</div>
      <nav>
        <router-link
          v-for="m in menus"
          :key="m.path"
          :to="m.path"
          class="nav-item"
          :class="{ active: route.path === m.path || (m.path !== '/' && route.path.startsWith(m.path)) }"
        >
          {{ m.title }}
        </router-link>
      </nav>
    </aside>

    <!-- 移动端顶部导航 -->
    <van-nav-bar v-if="isMobile" :title="currentTitle" fixed placeholder />

    <!-- 内容区 -->
    <main class="app-content" :class="{ 'with-tabbar': isMobile }">
      <router-view />
    </main>

    <!-- 移动端底部 tabbar -->
    <van-tabbar v-if="isMobile" route>
      <van-tabbar-item
        v-for="m in menus"
        :key="m.path"
        :to="m.path"
        :icon="m.icon"
      >
        {{ m.title }}
      </van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 220px;
  height: 100vh;
  background: #fff;
  border-right: 1px solid #ebedf0;
  padding: 24px 12px;
  z-index: 10;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 24px;
  padding: 0 12px;
}

.nav-item {
  display: block;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: 8px;
  color: #333;
  text-decoration: none;
  font-size: 15px;
}

.nav-item.active {
  background: #e8f3ff;
  color: #1989fa;
  font-weight: 600;
}

.app-content {
  padding: 16px;
  max-width: 1100px;
}

.app-content.with-tabbar {
  padding-bottom: 70px;
}

@media (min-width: 768px) {
  .app-content {
    margin-left: 220px;
    padding: 24px 32px;
  }
}
</style>
