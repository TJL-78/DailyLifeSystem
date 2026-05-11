<template>
  <div class="app-layout">
    <Sidebar />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from './stores/app'
import Sidebar from './components/Sidebar.vue'

const store = useAppStore()
onMounted(async () => {
  store.initTheme()
  await store.loadUser()
  await store.loadCategories()
})
</script>

<style>
.app-layout {
  display: flex;
  min-height: 100vh;
}
.main-content {
  flex: 1;
  margin-left: 240px;
  padding: 32px 40px;
  min-height: 100vh;
  overflow-y: auto;
}
</style>
