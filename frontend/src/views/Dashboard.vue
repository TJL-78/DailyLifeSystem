<template>
  <div class="dashboard">
    <h1 class="page-title">{{ t('dashTitle') }}</h1>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total || 0 }}</div>
        <div class="stat-label">{{ t('totalActs') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value stat-pending">{{ stats.pending || 0 }}</div>
        <div class="stat-label">{{ t('pending') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value stat-progress">{{ stats.in_progress || 0 }}</div>
        <div class="stat-label">{{ t('inProgress') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value stat-done">{{ stats.completed || 0 }}</div>
        <div class="stat-label">{{ t('completed') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value stat-rate">{{ completionRate }}%</div>
        <div class="stat-label">{{ t('completionRate') }}</div>
      </div>
    </div>

    <div class="dash-sections">
      <div class="dash-section">
        <h2 class="section-title">{{ t('todayTodo') }}</h2>
        <ul class="activity-list" v-if="todayActs.length">
          <ActivityItem v-for="a in todayActs" :key="a.id" :activity="a"
            @toggle="toggleActivity" @start="startActivity" @cancel="cancelActivity" @delete="deleteActivity" />
        </ul>
        <div v-else class="empty">{{ t('noTodayActs') }}</div>
      </div>
      <div class="dash-section">
        <h2 class="section-title">{{ t('recentActs') }}</h2>
        <ul class="activity-list" v-if="recentActs.length">
          <ActivityItem v-for="a in recentActs" :key="a.id" :activity="a"
            @toggle="toggleActivity" @start="startActivity" @cancel="cancelActivity" @delete="deleteActivity" />
        </ul>
        <div v-else class="empty">{{ t('noActs') }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from '../i18n'
import api from '../api'
import ActivityItem from '../components/ActivityItem.vue'

const { t } = useI18n()
const stats = ref({})
const todayActs = ref([])
const recentActs = ref([])

const completionRate = computed(() => {
  const total = stats.value.total || 0
  if (!total) return 0
  return Math.round(((stats.value.completed || 0) / total) * 100)
})

async function load() {
  stats.value = await api.getStats() || {}
  const today = new Date().toISOString().slice(0, 10)
  const all = await api.getActivities({ today: 1 }) || []
  todayActs.value = Array.isArray(all) ? all : (all.activities || [])
  const recent = await api.getActivities({}) || []
  const list = Array.isArray(recent) ? recent : (recent.activities || [])
  recentActs.value = list.slice(0, 10)
}

async function toggleActivity(a) {
  if (a.status === 'completed') return
  await api.completeActivity(a.id)
  await load()
}
async function startActivity(a) { await api.startActivity(a.id); await load() }
async function cancelActivity(a) { await api.cancelActivity(a.id); await load() }
async function deleteActivity(a) {
  if (!confirm(t('confirmDelete'))) return
  await api.deleteActivity(a.id); await load()
}

onMounted(load)
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.stats-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 32px; }
.stat-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; text-align: center; }
.stat-value { font-size: 28px; font-weight: 800; color: #1a1a2e; }
.stat-pending { color: #f59e0b; }
.stat-progress { color: #3b82f6; }
.stat-done { color: #10b981; }
.stat-rate { color: #4f46e5; }
.stat-label { font-size: 12px; color: #8b8fa8; margin-top: 4px; font-weight: 500; }
.dash-sections { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.section-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin-bottom: 14px; }
.activity-list { list-style: none; padding: 0; }
.empty { color: #b0b4c8; font-size: 13px; padding: 20px 0; text-align: center; }
</style>
