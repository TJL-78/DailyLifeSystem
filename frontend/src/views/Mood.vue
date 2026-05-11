<template>
  <div class="mood-page">
    <h1 class="page-title">{{ t('moodTitle') }}</h1>

    <div class="add-card">
      <h3>{{ t('addMoodRecord') }}</h3>
      <div class="form-row">
        <input type="date" v-model="form.record_date" />
        <div class="mood-picker">
          <span v-for="m in moods" :key="m.value" class="mood-btn" :class="{ active: form.mood === m.value }"
            @click="form.mood = m.value" :title="m.label">{{ m.emoji }}</span>
        </div>
      </div>
      <div class="form-row">
        <label>{{ t('energyLevel') }}</label>
        <div class="energy-bar">
          <span v-for="e in 5" :key="e" class="energy-dot" :class="{ active: form.energy >= e }" @click="form.energy = e">⚡</span>
        </div>
        <input v-model="form.note" :placeholder="t('notePlaceholder')" style="flex:1" />
        <button class="btn-primary" @click="addRecord">{{ t('add') }}</button>
      </div>
    </div>

    <!-- Mood calendar (last 30 days) -->
    <div class="chart-section" v-if="records.length">
      <h2 class="section-title">{{ t('moodCalendar') }}</h2>
      <div class="mood-grid">
        <div v-for="d in last30Days" :key="d" class="mood-day" :title="d">
          <span class="mood-day-emoji">{{ getMoodEmoji(d) }}</span>
          <span class="mood-day-date">{{ d.slice(8) }}</span>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats-grid" v-if="records.length">
      <div class="stat-card">
        <div class="stat-value stat-mood-icon">{{ topMoodEmoji }}</div>
        <div class="stat-label">{{ t('mostFrequentMood') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ avgEnergy }}</div>
        <div class="stat-label">{{ t('avgEnergy') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ records.length }}</div>
        <div class="stat-label">{{ t('totalRecords') }}</div>
      </div>
    </div>

    <!-- Records -->
    <div class="chart-section">
      <h2 class="section-title">{{ t('moodHistory') }}</h2>
      <div v-if="!records.length" class="empty">{{ t('noMoodRecords') }}</div>
      <div v-for="r in records" :key="r.id" class="record-item">
        <div class="record-date">{{ r.record_date }}</div>
        <span class="mood-emoji-lg">{{ moodMap[r.mood]?.emoji || '😐' }}</span>
        <span class="energy-display">{{ '⚡'.repeat(r.energy) }}</span>
        <span v-if="r.note" class="record-note-inline">{{ r.note }}</span>
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
const form = ref({ record_date: today, mood: 'happy', energy: 3, note: '' })
const records = ref([])

const moods = [
  { value: 'happy', emoji: '😊', label: '开心' },
  { value: 'excited', emoji: '🤩', label: '兴奋' },
  { value: 'calm', emoji: '😌', label: '平静' },
  { value: 'neutral', emoji: '😐', label: '一般' },
  { value: 'tired', emoji: '😴', label: '疲惫' },
  { value: 'sad', emoji: '😢', label: '难过' },
  { value: 'angry', emoji: '😤', label: '生气' },
  { value: 'anxious', emoji: '😰', label: '焦虑' },
]
const moodMap = Object.fromEntries(moods.map(m => [m.value, m]))

const last30Days = computed(() => {
  const days = []
  for (let i = 29; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    days.push(d.toISOString().slice(0, 10))
  }
  return days
})

const recordsByDate = computed(() => {
  const map = {}
  for (const r of records.value) map[r.record_date] = r
  return map
})

function getMoodEmoji(dateStr) {
  const r = recordsByDate.value[dateStr]
  return r ? (moodMap[r.mood]?.emoji || '😐') : '·'
}

const topMoodEmoji = computed(() => {
  if (!records.value.length) return '😐'
  const counts = {}
  for (const r of records.value) counts[r.mood] = (counts[r.mood] || 0) + 1
  const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0]
  return moodMap[top[0]]?.emoji || '😐'
})

const avgEnergy = computed(() => {
  if (!records.value.length) return '0'
  return (records.value.reduce((s, r) => s + r.energy, 0) / records.value.length).toFixed(1)
})

async function addRecord() {
  if (!form.value.record_date) return
  await api.createMood(form.value)
  form.value = { record_date: today, mood: 'happy', energy: 3, note: '' }
  await load()
}

async function deleteRecord(r) {
  if (!confirm(t('confirmDelete'))) return
  await api.deleteMood(r.id)
  await load()
}

async function load() {
  records.value = await api.getMood() || []
}

onMounted(load)
</script>

<style scoped>
.mood-page { max-width: 800px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.add-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; }
.add-card h3 { font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 12px; }
.form-row { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; flex-wrap: wrap; }
.form-row input { padding: 9px 14px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 13px; background: #fafbfd; }
.form-row label { font-size: 13px; font-weight: 500; color: #6b7085; }
.btn-primary { padding: 10px 20px; background: #4f46e5; color: #fff; border: none; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; }
.mood-picker { display: flex; gap: 4px; }
.mood-btn { font-size: 24px; cursor: pointer; padding: 4px; border-radius: 8px; border: 2px solid transparent; transition: all 0.15s; }
.mood-btn.active { border-color: #4f46e5; background: #f0f0ff; }
.mood-btn:hover { background: #f8f9fc; }
.energy-bar { display: flex; gap: 2px; }
.energy-dot { font-size: 18px; cursor: pointer; opacity: 0.3; transition: opacity 0.15s; }
.energy-dot.active { opacity: 1; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px; text-align: center; }
.stat-value { font-size: 28px; font-weight: 800; color: #4f46e5; }
.stat-mood-icon { font-size: 36px; }
.stat-label { font-size: 12px; color: #8b8fa8; margin-top: 4px; }
.chart-section { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; }
.section-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin-bottom: 14px; }
.mood-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 6px; }
.mood-day { text-align: center; }
.mood-day-emoji { font-size: 22px; display: block; }
.mood-day-date { font-size: 10px; color: #8b8fa8; }
.record-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f0f1f5; }
.record-date { font-size: 13px; font-weight: 600; color: #1a1a2e; min-width: 90px; }
.mood-emoji-lg { font-size: 22px; }
.energy-display { font-size: 14px; }
.record-note-inline { font-size: 12px; color: #8b8fa8; flex: 1; }
.btn-del { padding: 4px 12px; border: 1px solid #fecaca; border-radius: 6px; background: #fff; color: #ef4444; cursor: pointer; font-size: 11px; margin-left: auto; }
.empty { color: #b0b4c8; font-size: 13px; padding: 20px 0; text-align: center; }
</style>
