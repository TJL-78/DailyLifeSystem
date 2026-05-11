<template>
  <div class="goals-page">
    <h1 class="page-title">{{ t('goalsTitle') }}</h1>

    <div class="add-card">
      <h3>{{ t('addGoal') }}</h3>
      <div class="form-row">
        <input v-model="form.title" :placeholder="t('goalTitle')" class="input-main" />
        <input v-model.number="form.target_value" type="number" :placeholder="t('targetValue')" style="width:120px" />
        <input v-model="form.unit" :placeholder="t('goalUnit')" style="width:100px" />
        <select v-model="form.period">
          <option value="weekly">{{ t('goalWeekly') }}</option>
          <option value="monthly">{{ t('goalMonthly') }}</option>
          <option value="yearly">{{ t('goalYearly') }}</option>
        </select>
        <button class="btn-primary" @click="addGoal">{{ t('add') }}</button>
      </div>
    </div>

    <div v-if="!goals.length" class="empty">{{ t('noGoals') }}</div>

    <div v-for="g in goals" :key="g.id" class="goal-card">
      <div class="goal-header" @click="toggleExpand(g)">
        <div class="goal-info">
          <div class="goal-name">{{ g.title }}</div>
          <div class="goal-meta">{{ g.period }} · {{ g.current_value || 0 }}/{{ g.target_value }} {{ g.unit }}</div>
        </div>
        <div class="goal-actions">
          <button class="btn-del" @click.stop="deleteGoal(g)">{{ t('delete') }}</button>
        </div>
      </div>
      <div class="progress-bar-track">
        <div class="progress-bar-fill" :style="{ width: progressPct(g) + '%' }"></div>
      </div>
      <span class="progress-pct">{{ progressPct(g) }}%</span>

      <div v-if="g._expanded" class="goal-detail">
        <div class="progress-list">
          <div v-for="p in (g._progress || [])" :key="p.id" class="progress-entry">
            <span>+{{ p.value }} {{ g.unit }}</span>
            <span class="progress-date">{{ p.created_at?.slice(0, 10) }}</span>
          </div>
        </div>
        <div class="add-progress-row">
          <input v-model.number="g._addValue" type="number" :placeholder="t('progressValue')" />
          <button class="btn-primary" @click="addProgress(g)">{{ t('addProgress') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from '../i18n'
import api from '../api'

const { t } = useI18n()
const goals = ref([])
const form = ref({ title: '', target_value: 100, unit: '', period: 'monthly' })

function progressPct(g) {
  if (!g.target_value) return 0
  return Math.min(100, Math.round(((g.current_value || 0) / g.target_value) * 100))
}

async function load() {
  goals.value = (await api.getGoals() || []).map(g => ({ ...g, _expanded: false, _progress: [], _addValue: null }))
}

async function addGoal() {
  if (!form.value.title.trim() || !form.value.target_value) return
  await api.createGoal(form.value)
  form.value = { title: '', target_value: 100, unit: '', period: 'monthly' }
  await load()
}

async function deleteGoal(g) {
  if (!confirm(t('confirmDeleteGoal'))) return
  await api.deleteGoal(g.id)
  await load()
}

async function toggleExpand(g) {
  g._expanded = !g._expanded
  if (g._expanded) {
    g._progress = await api.getGoalProgress(g.id) || []
  }
}

async function addProgress(g) {
  if (!g._addValue) return
  await api.addGoalProgress(g.id, { value: g._addValue })
  g._addValue = null
  g._progress = await api.getGoalProgress(g.id) || []
  await load()
}

onMounted(load)
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.add-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; }
.add-card h3 { font-size: 14px; font-weight: 700; margin-bottom: 12px; color: #1a1a2e; }
.form-row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.form-row input, .form-row select { padding: 9px 14px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 13px; background: #fafbfd; }
.form-row input:focus, .form-row select:focus { outline: none; border-color: #4f46e5; background: #fff; }
.input-main { flex: 1; min-width: 200px; }
.btn-primary { padding: 10px 20px; background: #4f46e5; color: #fff; border: none; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; }
.goal-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 12px; }
.goal-header { display: flex; justify-content: space-between; align-items: flex-start; cursor: pointer; margin-bottom: 12px; }
.goal-name { font-size: 15px; font-weight: 700; color: #1a1a2e; }
.goal-meta { font-size: 12px; color: #8b8fa8; margin-top: 2px; }
.btn-del { padding: 6px 14px; border: 1px solid #fecaca; border-radius: 8px; background: #fff; color: #ef4444; cursor: pointer; font-size: 12px; }
.progress-bar-track { height: 8px; background: #f0f1f5; border-radius: 4px; overflow: hidden; }
.progress-bar-fill { height: 100%; background: #4f46e5; border-radius: 4px; transition: width 0.3s; }
.progress-pct { font-size: 12px; color: #8b8fa8; font-weight: 600; }
.goal-detail { margin-top: 16px; padding-top: 16px; border-top: 1px solid #eef0f4; }
.progress-entry { display: flex; justify-content: space-between; font-size: 13px; padding: 4px 0; color: #3a3a4e; }
.progress-date { color: #8b8fa8; }
.add-progress-row { display: flex; gap: 8px; margin-top: 12px; }
.add-progress-row input { padding: 8px 12px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 13px; width: 120px; background: #fafbfd; }
.add-progress-row input:focus { outline: none; border-color: #4f46e5; }
.empty { color: #b0b4c8; font-size: 13px; padding: 40px 0; text-align: center; }
</style>
