<template>
  <div class="sleep-page">
    <h1 class="page-title">{{ t('sleepTitle') }}</h1>

    <div class="add-card">
      <h3>{{ t('addSleepRecord') }}</h3>
      <div class="form-row">
        <input type="date" v-model="form.record_date" />
        <input type="time" v-model="form.sleep_time" :placeholder="t('sleepTimePh')" />
        <input type="time" v-model="form.wake_time" :placeholder="t('wakeTimePh')" />
      </div>
      <div class="form-row">
        <label>{{ t('sleepQuality') }}</label>
        <div class="quality-stars">
          <span v-for="s in 5" :key="s" class="star" :class="{ active: form.quality >= s }" @click="form.quality = s">★</span>
        </div>
        <input v-model="form.note" :placeholder="t('notePlaceholder')" style="flex:1" />
        <button class="btn-primary" @click="addRecord">{{ t('add') }}</button>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats-grid" v-if="records.length">
      <div class="stat-card">
        <div class="stat-value">{{ avgDuration }}</div>
        <div class="stat-label">{{ t('avgSleepHours') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ avgQuality }}</div>
        <div class="stat-label">{{ t('avgQuality') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ records.length }}</div>
        <div class="stat-label">{{ t('totalRecords') }}</div>
      </div>
    </div>

    <!-- Chart -->
    <div class="chart-section" v-if="records.length">
      <h2 class="section-title">{{ t('sleepTrend') }}</h2>
      <div class="sleep-chart">
        <div v-for="r in chartRecords" :key="r.id" class="chart-bar-col">
          <div class="chart-bar-wrap">
            <div class="chart-bar" :style="{ height: (r.duration_hours / 12 * 100) + '%' }"
              :class="qualityClass(r.quality)" :title="r.duration_hours + 'h'"></div>
          </div>
          <span class="chart-date">{{ r.record_date.slice(5) }}</span>
        </div>
      </div>
    </div>

    <!-- Records list -->
    <div class="chart-section">
      <h2 class="section-title">{{ t('sleepHistory') }}</h2>
      <div v-if="!records.length" class="empty">{{ t('noSleepRecords') }}</div>
      <div v-for="r in records" :key="r.id" class="record-item">
        <div class="record-date">{{ r.record_date }}</div>
        <div class="record-detail">
          <span v-if="r.sleep_time">🌙 {{ r.sleep_time }}</span>
          <span v-if="r.wake_time">☀️ {{ r.wake_time }}</span>
          <span>{{ r.duration_hours }}h</span>
          <span class="quality-display">{{ '★'.repeat(r.quality) }}{{ '☆'.repeat(5 - r.quality) }}</span>
        </div>
        <div v-if="r.note" class="record-note">{{ r.note }}</div>
        <button class="btn-del" @click="deleteRecord(r)">{{ t('delete') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from '../i18n'
import api from '../api'

const { t } = useI18n()
const today = new Date().toISOString().slice(0, 10)
const form = ref({ record_date: today, sleep_time: '23:00', wake_time: '07:00', quality: 3, note: '' })
const records = ref([])

const chartRecords = computed(() => [...records.value].reverse().slice(-14))
const avgDuration = computed(() => {
  if (!records.value.length) return '0'
  return (records.value.reduce((s, r) => s + r.duration_hours, 0) / records.value.length).toFixed(1)
})
const avgQuality = computed(() => {
  if (!records.value.length) return '0'
  return (records.value.reduce((s, r) => s + r.quality, 0) / records.value.length).toFixed(1)
})

function qualityClass(q) {
  if (q >= 4) return 'q-good'
  if (q >= 3) return 'q-ok'
  return 'q-bad'
}

function calcDuration(sleep, wake) {
  if (!sleep || !wake) return 0
  const [sh, sm] = sleep.split(':').map(Number)
  const [wh, wm] = wake.split(':').map(Number)
  let diff = (wh * 60 + wm) - (sh * 60 + sm)
  if (diff < 0) diff += 24 * 60
  return Math.round(diff / 60 * 10) / 10
}

async function addRecord() {
  if (!form.value.record_date) return
  const dur = calcDuration(form.value.sleep_time, form.value.wake_time)
  await api.createSleep({ ...form.value, duration_hours: dur })
  form.value = { record_date: today, sleep_time: '23:00', wake_time: '07:00', quality: 3, note: '' }
  await load()
}

async function deleteRecord(r) {
  if (!confirm(t('confirmDelete'))) return
  await api.deleteSleep(r.id)
  await load()
}

async function load() {
  records.value = await api.getSleep() || []
}

onMounted(load)
</script>

<style scoped>
.sleep-page { max-width: 800px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.add-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; }
.add-card h3 { font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 12px; }
.form-row { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; flex-wrap: wrap; }
.form-row input { padding: 9px 14px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 13px; background: #fafbfd; }
.form-row input:focus { outline: none; border-color: #4f46e5; }
.form-row label { font-size: 13px; font-weight: 500; color: #6b7085; }
.btn-primary { padding: 10px 20px; background: #4f46e5; color: #fff; border: none; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; }
.quality-stars { display: flex; gap: 2px; }
.star { font-size: 20px; color: #ddd; cursor: pointer; transition: color 0.15s; }
.star.active { color: #f59e0b; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px; text-align: center; }
.stat-value { font-size: 28px; font-weight: 800; color: #4f46e5; }
.stat-label { font-size: 12px; color: #8b8fa8; margin-top: 4px; }
.chart-section { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; }
.section-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin-bottom: 14px; }
.sleep-chart { display: flex; gap: 8px; align-items: flex-end; height: 120px; padding: 0 4px; }
.chart-bar-col { flex: 1; display: flex; flex-direction: column; align-items: center; }
.chart-bar-wrap { height: 100px; width: 100%; display: flex; align-items: flex-end; justify-content: center; }
.chart-bar { width: 16px; border-radius: 4px 4px 0 0; min-height: 4px; transition: height 0.3s; }
.q-good { background: #10b981; }
.q-ok { background: #f59e0b; }
.q-bad { background: #ef4444; }
.chart-date { font-size: 10px; color: #8b8fa8; margin-top: 4px; }
.record-item { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid #f0f1f5; flex-wrap: wrap; }
.record-date { font-size: 13px; font-weight: 600; color: #1a1a2e; min-width: 90px; }
.record-detail { display: flex; gap: 12px; font-size: 13px; color: #6b7085; flex: 1; }
.quality-display { color: #f59e0b; }
.record-note { font-size: 12px; color: #8b8fa8; width: 100%; padding-left: 102px; }
.btn-del { padding: 4px 12px; border: 1px solid #fecaca; border-radius: 6px; background: #fff; color: #ef4444; cursor: pointer; font-size: 11px; }
.empty { color: #b0b4c8; font-size: 13px; padding: 20px 0; text-align: center; }
</style>
