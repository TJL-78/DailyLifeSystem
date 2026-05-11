<template>
  <div class="report-page">
    <h2>{{ t('reportTitle') }}</h2>
    <div class="report-tabs">
      <button :class="{ active: reportType === 'daily' }" @click="reportType = 'daily'">{{ t('dailyReport') }}</button>
      <button :class="{ active: reportType === 'weekly' }" @click="reportType = 'weekly'">{{ t('weeklyReport') }}</button>
    </div>
    <div class="report-actions">
      <button class="btn-generate" @click="generate" :disabled="loading">
        {{ loading ? t('generating') : t('generateReport') }}
      </button>
      <button v-if="report" @click="copyToClipboard">{{ t('copyReport') }}</button>
      <button v-if="report" @click="exportMd">{{ t('exportMarkdown') }}</button>
    </div>

    <div v-if="copied" class="toast">{{ t('reportCopied') }}</div>

    <div v-if="!report && !loading" class="empty">{{ t('noReportData') }}</div>

    <div v-if="report" class="report-content">
      <div class="report-header">
        <span>{{ report.date_range }}</span>
      </div>
      <div v-for="section in report.sections" :key="section.title" class="report-card">
        <h3>{{ section.title }}</h3>
        <p>{{ section.content }}</p>
        <div v-if="section.stats" class="stats-grid">
          <div v-for="(val, key) in section.stats" :key="key" class="stat-item">
            <span class="stat-key">{{ key }}</span>
            <span class="stat-val">{{ val }}</span>
          </div>
        </div>
      </div>
      <div v-if="report.recommendations && report.recommendations.length" class="report-card recommendations">
        <h3>{{ t('recommendations') }}</h3>
        <ul>
          <li v-for="(rec, i) in report.recommendations" :key="i">{{ rec }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'
import { useI18n } from '../i18n'

const { t } = useI18n()
const reportType = ref('weekly')
const report = ref(null)
const loading = ref(false)
const copied = ref(false)

async function generate() {
  loading.value = true
  try {
    report.value = await api.getReport(reportType.value)
  } catch { report.value = null }
  loading.value = false
}

function copyToClipboard() {
  if (report.value?.raw_text) {
    navigator.clipboard.writeText(report.value.raw_text)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }
}

function exportMd() {
  if (!report.value?.raw_text) return
  const blob = new Blob([report.value.raw_text], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `report_${reportType.value}_${new Date().toISOString().slice(0, 10)}.md`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.report-page { padding: 24px; max-width: 800px; }
h2 { margin-bottom: 16px; }
.report-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.report-tabs button { padding: 8px 20px; border: 1px solid #ddd; border-radius: 6px; background: #fff; cursor: pointer; font-weight: 500; }
.report-tabs button.active { background: #4f46e5; color: #fff; border-color: #4f46e5; }
.report-actions { display: flex; gap: 8px; margin-bottom: 16px; }
.report-actions button { padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; background: #fff; cursor: pointer; }
.btn-generate { background: #4f46e5 !important; color: #fff !important; border-color: #4f46e5 !important; }
.btn-generate:disabled { opacity: 0.6; cursor: not-allowed; }
.empty { color: #999; text-align: center; padding: 40px; }
.toast { background: #10b981; color: #fff; padding: 8px 16px; border-radius: 6px; display: inline-block; margin-bottom: 12px; font-size: 13px; }
.report-content { margin-top: 8px; }
.report-header { font-size: 13px; color: #666; margin-bottom: 12px; }
.report-card { background: #fff; border: 1px solid #eef0f4; border-radius: 10px; padding: 20px; margin-bottom: 12px; }
.report-card h3 { font-size: 15px; margin-bottom: 8px; color: #1a1a2e; }
.report-card p { font-size: 13px; color: #555; line-height: 1.6; }
.stats-grid { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; }
.stat-item { background: #f8f9fc; padding: 8px 14px; border-radius: 6px; font-size: 12px; }
.stat-key { color: #888; margin-right: 6px; }
.stat-val { font-weight: 600; color: #1a1a2e; }
.recommendations ul { list-style: disc; padding-left: 20px; }
.recommendations li { font-size: 13px; color: #555; margin: 4px 0; }
</style>
