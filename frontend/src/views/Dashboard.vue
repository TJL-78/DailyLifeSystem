<template>
  <div class="dashboard">
    <div class="greeting-row">
      <div>
        <h1 class="page-title">{{ t('todayOverview') }}</h1>
        <p class="greeting-text">{{ data.greeting }} &mdash; {{ data.today }}</p>
      </div>
      <div class="quick-actions">
        <router-link to="/activities" class="qa-btn">{{ t('addActivityQuick') }}</router-link>
        <router-link to="/pomodoro" class="qa-btn qa-pomo">{{ t('startPomodoroQuick') }}</router-link>
        <router-link to="/journal" class="qa-btn qa-journal">{{ t('writeJournalQuick') }}</router-link>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value stat-pending">{{ data.stats?.pending || 0 }}</div>
        <div class="stat-label">{{ t('pending') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value stat-progress">{{ data.stats?.in_progress || 0 }}</div>
        <div class="stat-label">{{ t('inProgress') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value stat-done">{{ data.stats?.completed_today || 0 }}</div>
        <div class="stat-label">{{ t('completed') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value stat-pomo">{{ data.stats?.pomodoro_count || 0 }}</div>
        <div class="stat-label">{{ t('sessions') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value stat-focus">{{ data.stats?.focus_minutes || 0 }}</div>
        <div class="stat-label">{{ t('totalMinutes') }}</div>
      </div>
    </div>

    <div class="dash-sections">
      <div class="dash-section">
        <h2 class="section-title">{{ t('todayTodo') }}</h2>
        <ul class="activity-list" v-if="data.today_activities?.length">
          <ActivityItem v-for="a in data.today_activities" :key="a.id" :activity="a"
            @toggle="toggleActivity" @start="startActivity" @cancel="cancelActivity" @delete="deleteActivity" />
        </ul>
        <div v-else class="empty">{{ t('noTodayActs') }}</div>
      </div>

      <div class="dash-section">
        <h2 class="section-title">{{ t('recentActs') }}</h2>
        <ul class="activity-list" v-if="data.recent_completed?.length">
          <ActivityItem v-for="a in data.recent_completed" :key="a.id" :activity="a"
            @toggle="toggleActivity" @start="startActivity" @cancel="cancelActivity" @delete="deleteActivity" />
        </ul>
        <div v-else class="empty">{{ t('noActs') }}</div>
      </div>

      <div class="dash-section">
        <h2 class="section-title">{{ t('activeHabits') }}</h2>
        <div v-if="data.habits?.length" class="habit-list">
          <div v-for="h in data.habits" :key="h.id" class="habit-row">
            <span class="habit-dot" :style="{ background: h.color }"></span>
            <span class="habit-name">{{ h.name }}</span>
            <span class="badge" :class="h.checked_today ? 'badge-done' : 'badge-not'">
              {{ h.checked_today ? t('checkedToday') : t('pending') }}
            </span>
          </div>
        </div>
        <div v-else class="empty">{{ t('noHabits') }}</div>
      </div>

      <div class="dash-section">
        <h2 class="section-title">{{ t('activeGoals') }}</h2>
        <div v-if="data.goals?.length" class="goal-list">
          <div v-for="g in data.goals" :key="g.id" class="goal-row">
            <div class="goal-header">
              <span class="goal-name">{{ g.title }}</span>
              <span class="goal-pct">{{ g.progress_pct }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: g.progress_pct + '%' }"></div>
            </div>
            <div class="goal-detail">{{ g.current_value }} / {{ g.target_value }} {{ g.unit }}</div>
          </div>
        </div>
        <div v-else class="empty">{{ t('noGoals') }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from '../i18n'
import api from '../api'
import ActivityItem from '../components/ActivityItem.vue'

const { t } = useI18n()
const data = ref({})

async function load() {
  try { await api.generateRecurring() } catch (e) { /* ignore */ }
  data.value = await api.getDashboard() || {}
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
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 4px; }
.greeting-row { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.greeting-text { font-size: 14px; color: #8b8fa8; }
.quick-actions { display: flex; gap: 8px; }
.qa-btn { padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; text-decoration: none; background: #4f46e5; color: #fff; }
.qa-pomo { background: #10b981; }
.qa-journal { background: #f59e0b; color: #1a1a2e; }
.stats-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 32px; }
.stat-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; text-align: center; }
.stat-value { font-size: 28px; font-weight: 800; color: #1a1a2e; }
.stat-pending { color: #f59e0b; }
.stat-progress { color: #3b82f6; }
.stat-done { color: #10b981; }
.stat-pomo { color: #ef4444; }
.stat-focus { color: #4f46e5; }
.stat-label { font-size: 12px; color: #8b8fa8; margin-top: 4px; font-weight: 500; }
.dash-sections { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.dash-section { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; }
.section-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin-bottom: 14px; }
.activity-list { list-style: none; padding: 0; }
.empty { color: #b0b4c8; font-size: 13px; padding: 20px 0; text-align: center; }
.habit-list { display: flex; flex-direction: column; gap: 8px; }
.habit-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f0f1f5; font-size: 13px; }
.habit-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.habit-name { flex: 1; font-weight: 500; color: #1a1a2e; }
.badge { display: inline-flex; padding: 2px 10px; border-radius: 100px; font-size: 11px; font-weight: 600; }
.badge-done { background: #ecfdf5; color: #059669; }
.badge-not { background: #fffbeb; color: #d97706; }
.goal-list { display: flex; flex-direction: column; gap: 14px; }
.goal-row { }
.goal-header { display: flex; justify-content: space-between; margin-bottom: 4px; }
.goal-name { font-size: 13px; font-weight: 600; color: #1a1a2e; }
.goal-pct { font-size: 13px; font-weight: 700; color: #4f46e5; }
.progress-bar { height: 8px; background: #eef0f4; border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: #4f46e5; border-radius: 4px; transition: width 0.3s; }
.goal-detail { font-size: 11px; color: #8b8fa8; margin-top: 2px; }
</style>
