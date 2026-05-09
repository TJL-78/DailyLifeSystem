<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <h2>{{ t('appTitle') }}</h2>
      <small>Daily Life System</small>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/" class="nav-item" :class="{ active: $route.name === 'dashboard' }">
        <span class="nav-icon">◻</span><span>{{ t('dashboard') }}</span>
      </router-link>
      <router-link to="/activities" class="nav-item" :class="{ active: $route.name === 'activities' }">
        <span class="nav-icon">☰</span><span>{{ t('allActivities') }}</span>
      </router-link>
      <router-link to="/calendar" class="nav-item" :class="{ active: $route.name === 'calendar' }">
        <span class="nav-icon">○</span><span>{{ t('calendarView') }}</span>
      </router-link>
      <router-link to="/habits" class="nav-item" :class="{ active: $route.name === 'habits' }">
        <span class="nav-icon">★</span><span>{{ t('habitTrack') }}</span>
      </router-link>
      <router-link to="/journal" class="nav-item" :class="{ active: $route.name === 'journal' }">
        <span class="nav-icon">✎</span><span>{{ t('journalNav') }}</span>
      </router-link>
      <router-link to="/statistics" class="nav-item" :class="{ active: $route.name === 'statistics' }">
        <span class="nav-icon">▲</span><span>{{ t('statistics') }}</span>
      </router-link>
      <div class="nav-section">{{ t('categoryLabel') }}</div>
      <router-link v-for="cat in store.categories" :key="cat.id"
        :to="'/activities?category=' + cat.id" class="nav-item">
        <span class="cat-dot" :style="{ background: cat.color }"></span>
        <span>{{ cat.icon }} {{ cat.name }}</span>
      </router-link>
      <router-link to="/categories" class="nav-item" :class="{ active: $route.name === 'categories' }">
        <span class="nav-icon">⚙</span><span>{{ t('manageCategories') }}</span>
      </router-link>
      <router-link to="/settings" class="nav-item" :class="{ active: $route.name === 'settings' }">
        <span class="nav-icon">⚙</span><span>{{ t('settingsNav') }}</span>
      </router-link>
    </nav>
    <div class="user-section">
      <div class="user-row">
        <div class="user-avatar">
          <img v-if="store.user?.avatar_url" :src="store.user.avatar_url" />
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </div>
        <span class="username">{{ store.user?.display_name || store.user?.username || '' }}</span>
      </div>
      <button class="btn-logout" @click="store.logout()">{{ t('logout') }}</button>
    </div>
  </aside>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import { useI18n } from '../i18n'
const store = useAppStore()
const { t } = useI18n()
</script>

<style scoped>
.sidebar { width: 240px; background: #fff; border-right: 1px solid #eef0f4; display: flex; flex-direction: column; position: fixed; top: 0; left: 0; bottom: 0; z-index: 100; }
.sidebar-brand { padding: 28px 24px 20px; border-bottom: 1px solid #eef0f4; }
.sidebar-brand h2 { font-size: 17px; font-weight: 700; color: #1a1a2e; }
.sidebar-brand small { font-size: 11px; color: #a0a4b8; }
.sidebar-nav { flex: 1; padding: 12px 0; overflow-y: auto; }
.nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 24px; color: #6b7085; font-size: 13px; font-weight: 500; text-decoration: none; border-left: 2px solid transparent; transition: all 0.15s; }
.nav-item:hover { color: #1a1a2e; background: #f8f9fc; text-decoration: none; }
.nav-item.active, .nav-item.router-link-exact-active { color: #4f46e5; background: #f0f0ff; border-left-color: #4f46e5; font-weight: 600; }
.nav-icon { width: 18px; text-align: center; font-size: 14px; flex-shrink: 0; }
.nav-section { padding: 20px 24px 8px; font-size: 10px; text-transform: uppercase; color: #b0b4c8; letter-spacing: 1.5px; font-weight: 700; }
.cat-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.user-section { padding: 16px 24px; border-top: 1px solid #eef0f4; background: #fafbfd; }
.user-row { display: flex; align-items: center; gap: 10px; }
.user-avatar { width: 32px; height: 32px; border-radius: 50%; background: #eef0f4; overflow: hidden; display: flex; align-items: center; justify-content: center; color: #8b8fa8; flex-shrink: 0; }
.user-avatar img { width: 100%; height: 100%; object-fit: cover; }
.username { font-size: 13px; color: #1a1a2e; font-weight: 500; }
.btn-logout { background: none; border: none; color: #e74c3c; cursor: pointer; font-size: 11px; margin-top: 6px; font-weight: 500; }
</style>
