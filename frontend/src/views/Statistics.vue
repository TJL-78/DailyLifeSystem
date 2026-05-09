<template>
  <div class="stats-page">
    <h1 class="page-title">{{ t('statsTitle') }}</h1>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ detailed.total_completed || 0 }}</div>
        <div class="stat-label">{{ t('totalCompleted') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ totalTimeStr }}</div>
        <div class="stat-label">{{ t('totalTime') }}</div>
      </div>
    </div>

    <div class="chart-section">
      <h2 class="section-title">{{ t('catDistribution') }}</h2>
      <div v-if="catData.length" class="bar-chart">
        <div v-for="c in catData" :key="c.name" class="bar-row">
          <span class="bar-label">{{ c.name }}</span>
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: c.pct + '%', background: c.color }"></div>
          </div>
          <span class="bar-value">{{ c.count }}</span>
        </div>
      </div>
      <div v-else class="empty">{{ t('noData') }}</div>
    </div>

    <div class="chart-section">
      <h2 class="section-title">{{ t('weeklyTrend') }}</h2>
      <div v-if="weeklyData.length" class="weekly-chart">
        <div v-for="(w, i) in weeklyData" :key="i" class="week-col">
          <div class="week-bars">
            <div class="week-bar bar-new" :style="{ height: barHeight(w.new_count) + 'px' }" :title="t('newAdded') + ': ' + w.new_count"></div>
            <div class="week-bar bar-done" :style="{ height: barHeight(w.completed_count) + 'px' }" :title="t('completedLabel') + ': ' + w.completed_count"></div>
          </div>
          <span class="week-label">{{ t('weekLabel') }}{{ i + 1 }}</span>
        </div>
      </div>
      <div v-else class="empty">{{ t('noData') }}</div>
    </div>

    <div class="chart-section">
      <h2 class="section-title">{{ t('catTimeTitle') }}</h2>
      <div v-if="timeData.length" class="time-chart">
        <svg viewBox="0 0 200 200" class="pie-svg">
          <circle v-for="(s, i) in pieSlices" :key="i"
            cx="100" cy="100" r="80"
            fill="none" :stroke="s.color" stroke-width="30"
            :stroke-dasharray="s.dash" :stroke-dashoffset="s.offset"
          />
        </svg>
        <div class="time-legend">
          <div v-for="d in timeData" :key="d.name" class="legend-item">
            <span class="legend-dot" :style="{ background: d.color }"></span>
            <span>{{ d.name }}: {{ d.minutes }}{{ t('minutes') }} ({{ d.pct }}%)</span>
          </div>
          <div class="legend-total">{{ t('totalTime2') }}: {{ totalMinutes }}{{ t('minutes') }}</div>
        </div>
      </div>
      <div v-else class="empty">{{ t('noTimeData') }}</div>
    </div>

    <div class="export-section">
      <button class="btn-export" @click="exportJSON">{{ t('exportJSON') }}</button>
      <button class="btn-export" @click="exportCSV">{{ t('exportCSV') }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from '../i18n'
import { useAppStore } from '../stores/app'
import api from '../api'

const { t } = useI18n()
const store = useAppStore()
const detailed = ref({})
const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

const totalTimeStr = computed(() => {
  const m = detailed.value.total_time || 0
  if (m < 60) return m + t('minutes')
  return Math.floor(m / 60) + 'h ' + (m % 60) + 'm'
})

const catData = computed(() => {
  const dist = detailed.value.category_distribution || {}
  const entries = Object.entries(dist)
  const max = Math.max(...entries.map(([, v]) => v), 1)
  return entries.map(([name, count], i) => ({ name: name || t('unclassified'), count, pct: Math.round((count / max) * 100), color: colors[i % colors.length] }))
})

const weeklyData = computed(() => detailed.value.weekly_trend || [])

const timeData = computed(() => {
  const ct = detailed.value.category_time || {}
  const entries = Object.entries(ct).filter(([, v]) => v > 0)
  const total = entries.reduce((s, [, v]) => s + v, 0)
  return entries.map(([name, minutes], i) => ({ name: name || t('unclassified'), minutes, pct: Math.round((minutes / total) * 100), color: colors[i % colors.length] }))
})

const totalMinutes = computed(() => timeData.value.reduce((s, d) => s + d.minutes, 0))

const pieSlices = computed(() => {
  const circ = 2 * Math.PI * 80
  let offset = 0
  return timeData.value.map(d => {
    const dash = (d.pct / 100) * circ
    const slice = { color: d.color, dash: `${dash} ${circ - dash}`, offset: -offset + circ / 4 }
    offset += dash
    return slice
  })
})

function barHeight(v) { return Math.min(Math.max(v * 8, 4), 120) }

async function load() {
  detailed.value = await api.getDetailedStats() || {}
}

function download(content, filename) {
  const blob = new Blob([content], { type: 'text/plain' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  a.click()
}

async function exportJSON() {
  const acts = await api.getActivities({})
  const list = Array.isArray(acts) ? acts : (acts?.activities || [])
  download(JSON.stringify(list, null, 2), 'activities.json')
}

async function exportCSV() {
  const acts = await api.getActivities({})
  const list = Array.isArray(acts) ? acts : (acts?.activities || [])
  if (!list.length) return
  const headers = Object.keys(list[0])
  const rows = [headers.join(','), ...list.map(a => headers.map(h => JSON.stringify(a[h] ?? '')).join(','))]
  download(rows.join('\n'), 'activities.csv')
}

onMounted(load)
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.section-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin-bottom: 14px; }
.stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 32px; }
.stat-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 24px; text-align: center; }
.stat-value { font-size: 32px; font-weight: 800; color: #4f46e5; }
.stat-label { font-size: 12px; color: #8b8fa8; margin-top: 4px; font-weight: 500; }
.chart-section { background: #fff; border: 1px solid #eef0f4; border-radius: 16px; padding: 24px 28px; margin-bottom: 20px; }
.bar-chart { }
.bar-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.bar-label { font-size: 12px; font-weight: 600; color: #6b7085; width: 80px; text-align: right; flex-shrink: 0; }
.bar-track { flex: 1; height: 20px; background: #f0f1f5; border-radius: 10px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 10px; transition: width 0.3s; }
.bar-value { font-size: 12px; font-weight: 700; color: #1a1a2e; width: 30px; }
.weekly-chart { display: flex; gap: 16px; justify-content: center; align-items: flex-end; padding: 20px 0; }
.week-col { text-align: center; }
.week-bars { display: flex; gap: 4px; align-items: flex-end; justify-content: center; }
.week-bar { width: 20px; border-radius: 4px 4px 0 0; min-height: 4px; }
.bar-new { background: #4f46e5; }
.bar-done { background: #10b981; }
.week-label { font-size: 11px; color: #8b8fa8; margin-top: 6px; display: block; }
.time-chart { display: flex; gap: 32px; align-items: center; }
.pie-svg { width: 160px; height: 160px; flex-shrink: 0; }
.time-legend { flex: 1; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #3a3a4e; margin-bottom: 6px; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.legend-total { font-size: 13px; font-weight: 700; color: #1a1a2e; margin-top: 8px; }
.export-section { display: flex; gap: 8px; }
.btn-export { padding: 10px 24px; background: #fff; border: 1px solid #eef0f4; border-radius: 10px; font-size: 13px; font-weight: 600; color: #4f46e5; cursor: pointer; }
.btn-export:hover { background: #f0f0ff; }
.empty { color: #b0b4c8; font-size: 13px; padding: 20px 0; text-align: center; }
</style>
