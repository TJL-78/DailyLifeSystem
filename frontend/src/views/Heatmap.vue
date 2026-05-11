<template>
  <div class="heatmap-page">
    <h1 class="page-title">{{ t('heatmapTitle') }}</h1>

    <div class="heatmap-card">
      <div class="year-nav">
        <button @click="year--; loadHeatmap()">◀</button>
        <span class="year-label">{{ year }}</span>
        <button @click="year++; loadHeatmap()">▶</button>
      </div>
      <div class="heatmap-grid">
        <div class="heatmap-row" v-for="day in 7" :key="day">
          <div v-for="week in 53" :key="week"
            class="heatmap-cell"
            :style="{ background: cellColor(day - 1, week - 1) }"
            :title="cellTitle(day - 1, week - 1)">
          </div>
        </div>
      </div>
      <div class="heatmap-legend">
        <span>{{ t('lessActive') }}</span>
        <div class="legend-cell" style="background:#ebedf0"></div>
        <div class="legend-cell" style="background:#9be9a8"></div>
        <div class="legend-cell" style="background:#40c463"></div>
        <div class="legend-cell" style="background:#30a14e"></div>
        <div class="legend-cell" style="background:#216e39"></div>
        <span>{{ t('moreActive') }}</span>
      </div>
    </div>

    <div class="report-card">
      <h2 class="section-title">{{ t('monthlyReport') }}</h2>
      <div class="month-nav">
        <select v-model="reportYear" @change="loadReport()">
          <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
        </select>
        <select v-model="reportMonth" @change="loadReport()">
          <option v-for="m in 12" :key="m" :value="m">{{ m }}</option>
        </select>
      </div>
      <div class="report-stats" v-if="report">
        <div class="stat-card">
          <div class="stat-value">{{ report.total_activities || 0 }}</div>
          <div class="stat-label">{{ t('activitiesCount') }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ report.completed || 0 }}</div>
          <div class="stat-label">{{ t('completed') }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ report.total_minutes || 0 }}</div>
          <div class="stat-label">{{ t('totalMinutes') }}</div>
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
const now = new Date()
const year = ref(now.getFullYear())
const heatmapData = ref({})
const reportYear = ref(now.getFullYear())
const reportMonth = ref(now.getMonth() + 1)
const report = ref(null)
const yearOptions = Array.from({ length: 5 }, (_, i) => now.getFullYear() - i)

function dateForCell(dayOfWeek, weekIndex) {
  const jan1 = new Date(year.value, 0, 1)
  const startDay = jan1.getDay()
  const dayOffset = weekIndex * 7 + dayOfWeek - startDay
  const d = new Date(year.value, 0, 1 + dayOffset)
  if (d.getFullYear() !== year.value) return null
  return d.toISOString().slice(0, 10)
}

function cellColor(dayOfWeek, weekIndex) {
  const date = dateForCell(dayOfWeek, weekIndex)
  if (!date) return 'transparent'
  const count = heatmapData.value[date] || 0
  if (count === 0) return '#ebedf0'
  if (count <= 2) return '#9be9a8'
  if (count <= 4) return '#40c463'
  if (count <= 6) return '#30a14e'
  return '#216e39'
}

function cellTitle(dayOfWeek, weekIndex) {
  const date = dateForCell(dayOfWeek, weekIndex)
  if (!date) return ''
  const count = heatmapData.value[date] || 0
  return `${date}: ${count} ${t('activitiesCount')}`
}

async function loadHeatmap() {
  heatmapData.value = await api.getHeatmapData(year.value) || {}
}

async function loadReport() {
  report.value = await api.getMonthlyReport(reportYear.value, reportMonth.value) || {}
}

onMounted(() => { loadHeatmap(); loadReport() })
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.section-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin-bottom: 14px; }
.heatmap-card { background: #fff; border: 1px solid #eef0f4; border-radius: 16px; padding: 24px 28px; margin-bottom: 24px; }
.year-nav { display: flex; align-items: center; gap: 16px; justify-content: center; margin-bottom: 20px; }
.year-nav button { padding: 6px 14px; border: 1px solid #eef0f4; border-radius: 8px; background: #fff; cursor: pointer; font-size: 14px; color: #6b7085; }
.year-label { font-size: 18px; font-weight: 700; color: #1a1a2e; }
.heatmap-grid { overflow-x: auto; }
.heatmap-row { display: flex; gap: 2px; margin-bottom: 2px; }
.heatmap-cell { width: 12px; height: 12px; border-radius: 2px; flex-shrink: 0; }
.heatmap-legend { display: flex; align-items: center; gap: 4px; margin-top: 12px; font-size: 11px; color: #8b8fa8; }
.legend-cell { width: 12px; height: 12px; border-radius: 2px; }
.report-card { background: #fff; border: 1px solid #eef0f4; border-radius: 16px; padding: 24px 28px; }
.month-nav { display: flex; gap: 8px; margin-bottom: 20px; }
.month-nav select { padding: 8px 14px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 13px; background: #fff; }
.report-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.stat-card { background: #fafbfd; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px; text-align: center; }
.stat-value { font-size: 28px; font-weight: 800; color: #4f46e5; }
.stat-label { font-size: 12px; color: #8b8fa8; margin-top: 4px; font-weight: 500; }
</style>
