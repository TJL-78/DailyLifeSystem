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
          <span class="week-label">{{ formatWeekLabel(w) }}</span>
        </div>
      </div>
      <div v-else class="empty">{{ t('noData') }}</div>
    </div>

    <div class="chart-section">
      <h2 class="section-title">{{ t('catTimeTitle') }}</h2>
      <div v-if="categoryDetails.length" class="category-pies">
        <div v-for="(cat, ci) in categoryDetails" :key="cat.name" class="cat-pie-card">
          <div class="cat-pie-header">
            <div class="cat-pie-wrap">
              <svg viewBox="0 0 120 120" class="cat-pie-svg" :class="{ spinning: cat._spinning }" @click="toggleSpin(ci)">
                <circle v-for="(s, si) in cat.slices" :key="si"
                  cx="60" cy="60" r="50"
                  fill="none" :stroke="s.color" stroke-width="20"
                  :stroke-dasharray="s.dash" :stroke-dashoffset="s.offset"
                  class="pie-slice"
                  @mouseenter="showTooltip($event, cat, si, ci)"
                  @mouseleave="hideTooltip"
                />
              </svg>
              <div v-if="tooltip.visible && tooltip.catIndex === ci" class="pie-tooltip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
                <div class="tooltip-name">{{ tooltip.name }}</div>
                <div class="tooltip-detail">{{ tooltip.minutes }}{{ t('minutes') }} ({{ tooltip.pct }}%)</div>
              </div>
            </div>
            <div class="cat-pie-info">
              <div class="cat-pie-name" :style="{ color: cat.color }">{{ cat.name }}</div>
              <div class="cat-pie-total">{{ cat.total_minutes }}{{ t('minutes') }}</div>
              <div class="cat-pie-count">{{ cat.tasks.length }} {{ t('tasks') }}</div>
            </div>
          </div>
          <div class="cat-task-list">
            <div v-for="(task, ti) in cat.tasks" :key="ti" class="cat-task-item">
              <span class="cat-task-dot" :style="{ background: taskColors[ti % taskColors.length] }"></span>
              <span class="cat-task-title">{{ task.title }}</span>
              <span class="cat-task-time">{{ task.minutes }}{{ t('minutes') }}</span>
              <span class="cat-task-status" :class="'status-' + task.status">{{ t(task.status) || task.status }}</span>
            </div>
          </div>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from '../i18n'
import { useAppStore } from '../stores/app'
import api from '../api'

const { t } = useI18n()
const store = useAppStore()
const detailed = ref({})
const tooltip = reactive({ visible: false, name: '', minutes: 0, pct: '', x: 0, y: 0, catIndex: -1 })
const spinningSet = ref(new Set())

function showTooltip(event, cat, sliceIndex, catIndex) {
  const task = cat.tasks[sliceIndex]
  if (!task) return
  const total = cat.total_minutes || 1
  const rect = event.target.closest('.cat-pie-wrap').getBoundingClientRect()
  tooltip.name = task.title
  tooltip.minutes = task.minutes
  tooltip.pct = ((task.minutes / total) * 100).toFixed(1)
  tooltip.x = event.clientX - rect.left + 10
  tooltip.y = event.clientY - rect.top - 30
  tooltip.catIndex = catIndex
  tooltip.visible = true
}

function hideTooltip() {
  tooltip.visible = false
}

function toggleSpin(ci) {
  // Remove first to allow re-trigger
  spinningSet.value.delete(ci)
  spinningSet.value = new Set(spinningSet.value)
  // Use nextTick to re-add so animation restarts
  requestAnimationFrame(() => {
    spinningSet.value.add(ci)
    spinningSet.value = new Set(spinningSet.value)
    // Auto-remove after animation ends (2s)
    setTimeout(() => {
      spinningSet.value.delete(ci)
      spinningSet.value = new Set(spinningSet.value)
    }, 2000)
  })
}
const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
const taskColors = ['#6366f1', '#14b8a6', '#f97316', '#e11d48', '#a855f7', '#0ea5e9', '#eab308', '#22c55e', '#f43f5e', '#8b5cf6']

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

const categoryDetails = computed(() => {
  const details = detailed.value.category_time_detail || []
  return details.map((cat, ci) => {
    const circ = 2 * Math.PI * 50
    const total = cat.total_minutes || 1
    let offset = 0
    const slices = cat.tasks.map((task, ti) => {
      const pct = task.minutes / total
      const dash = pct * circ
      const slice = { color: taskColors[ti % taskColors.length], dash: `${dash} ${circ - dash}`, offset: -offset + circ / 4 }
      offset += dash
      return slice
    })
    return {
      name: cat.name,
      color: cat.color || colors[ci % colors.length],
      total_minutes: cat.total_minutes,
      tasks: cat.tasks,
      slices,
      _spinning: spinningSet.value.has(ci),
    }
  })
})

function barHeight(v) { return Math.min(Math.max(v * 8, 4), 120) }

function formatWeekLabel(w) {
  if (w.week) {
    const d = new Date(w.week)
    return `${d.getMonth() + 1}/${d.getDate()}`
  }
  return ''
}

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
.export-section { display: flex; gap: 8px; }
.btn-export { padding: 10px 24px; background: #fff; border: 1px solid #eef0f4; border-radius: 10px; font-size: 13px; font-weight: 600; color: #4f46e5; cursor: pointer; }
.btn-export:hover { background: #f0f0ff; }
.empty { color: #b0b4c8; font-size: 13px; padding: 20px 0; text-align: center; }
.category-pies { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.cat-pie-card { background: #fafbfd; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px; }
.cat-pie-header { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
.cat-pie-svg { width: 100px; height: 100px; flex-shrink: 0; cursor: pointer; transition: transform 0.3s; }
.cat-pie-svg.spinning { animation: pie-spin 2s ease-in-out forwards; }
@keyframes pie-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.cat-pie-wrap { position: relative; flex-shrink: 0; }
.pie-slice { cursor: pointer; transition: opacity 0.2s; }
.pie-slice:hover { opacity: 0.7; stroke-width: 24; }
.pie-tooltip { position: absolute; background: rgba(26,26,46,0.92); color: #fff; padding: 6px 12px; border-radius: 8px; font-size: 12px; pointer-events: none; white-space: nowrap; z-index: 10; }
.tooltip-name { font-weight: 700; }
.tooltip-detail { font-size: 11px; color: #c4c8e0; margin-top: 2px; }
.cat-pie-info { flex: 1; }
.cat-pie-name { font-size: 16px; font-weight: 700; }
.cat-pie-total { font-size: 20px; font-weight: 800; color: #1a1a2e; margin-top: 2px; }
.cat-pie-count { font-size: 12px; color: #8b8fa8; margin-top: 2px; }
.cat-task-list { border-top: 1px solid #eef0f4; padding-top: 12px; }
.cat-task-item { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 12px; }
.cat-task-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.cat-task-title { flex: 1; color: #3a3a4e; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cat-task-time { color: #6b7085; font-weight: 600; flex-shrink: 0; }
.cat-task-status { padding: 1px 8px; border-radius: 100px; font-size: 10px; font-weight: 600; flex-shrink: 0; }
.status-completed { background: #ecfdf5; color: #059669; }
.status-pending { background: #fffbeb; color: #d97706; }
.status-in_progress { background: #eef2ff; color: #4f46e5; }
.status-cancelled { background: #f3f4f6; color: #9ca3af; }
</style>
