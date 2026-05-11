<template>
  <div class="health-page">
    <h1 class="page-title">{{ t('healthTitle') }}</h1>

    <div class="add-card">
      <h3>{{ t('addHealthRecord') }}</h3>
      <div class="form-row">
        <input type="date" v-model="form.record_date" />
        <select v-model="form.exercise_type">
          <option value="">{{ t('exerciseType') }}</option>
          <option value="running">🏃 {{ t('running') }}</option>
          <option value="walking">🚶 {{ t('walking') }}</option>
          <option value="gym">🏋️ {{ t('gym') }}</option>
          <option value="yoga">🧘 {{ t('yoga') }}</option>
          <option value="cycling">🚴 {{ t('cycling') }}</option>
          <option value="swimming">🏊 {{ t('swimming') }}</option>
          <option value="other">{{ t('otherExercise') }}</option>
        </select>
        <input type="number" v-model.number="form.exercise_minutes" :placeholder="t('exerciseMinPh')" min="0" style="width:100px" />
      </div>
      <div class="form-row">
        <div class="water-section">
          <label>💧 {{ t('waterIntake') }}</label>
          <div class="water-btns">
            <button v-for="ml in [250, 500, 750]" :key="ml" class="water-btn" @click="form.water_ml += ml">+{{ ml }}ml</button>
          </div>
          <span class="water-total">{{ form.water_ml }}ml</span>
          <button class="water-reset" @click="form.water_ml = 0">{{ t('resetTimer') }}</button>
        </div>
      </div>
      <div class="form-row">
        <input type="number" v-model.number="form.steps" :placeholder="t('stepsPlaceholder')" min="0" style="width:120px" />
        <input type="number" v-model.number="form.weight_kg" :placeholder="t('weightPlaceholder')" min="0" step="0.1" style="width:120px" />
        <input v-model="form.note" :placeholder="t('notePlaceholder')" style="flex:1" />
        <button class="btn-primary" @click="addRecord">{{ t('add') }}</button>
      </div>
    </div>

    <!-- Today's Summary -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value stat-exercise">{{ todayExercise }}</div>
        <div class="stat-label">{{ t('todayExerciseMin') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value stat-water">{{ todayWater }}</div>
        <div class="stat-label">{{ t('todayWaterMl') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value stat-steps">{{ todaySteps }}</div>
        <div class="stat-label">{{ t('todaySteps') }}</div>
      </div>
    </div>

    <!-- Water progress bar -->
    <div class="chart-section" v-if="todayWater > 0">
      <h2 class="section-title">💧 {{ t('waterProgress') }}</h2>
      <div class="water-progress">
        <div class="water-fill" :style="{ width: Math.min(todayWater / 2000 * 100, 100) + '%' }"></div>
      </div>
      <div class="water-label">{{ todayWater }} / 2000 ml ({{ Math.round(todayWater / 2000 * 100) }}%)</div>
    </div>

    <!-- Records -->
    <div class="chart-section">
      <h2 class="section-title">{{ t('healthHistory') }}</h2>
      <div v-if="!records.length" class="empty">{{ t('noHealthRecords') }}</div>
      <div v-for="r in records" :key="r.id" class="record-item">
        <div class="record-date">{{ r.record_date }}</div>
        <div class="record-detail">
          <span v-if="r.exercise_type">{{ exerciseEmoji(r.exercise_type) }} {{ r.exercise_minutes }}{{ t('minutes') }}</span>
          <span v-if="r.water_ml">💧 {{ r.water_ml }}ml</span>
          <span v-if="r.steps">👟 {{ r.steps }}</span>
          <span v-if="r.weight_kg">⚖️ {{ r.weight_kg }}kg</span>
        </div>
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
const form = ref({ record_date: today, exercise_type: '', exercise_minutes: 0, water_ml: 0, steps: 0, weight_kg: 0, note: '' })
const records = ref([])

const todayRecords = computed(() => records.value.filter(r => r.record_date === today))
const todayExercise = computed(() => todayRecords.value.reduce((s, r) => s + (r.exercise_minutes || 0), 0))
const todayWater = computed(() => todayRecords.value.reduce((s, r) => s + (r.water_ml || 0), 0))
const todaySteps = computed(() => todayRecords.value.reduce((s, r) => s + (r.steps || 0), 0))

const exerciseEmojis = { running: '🏃', walking: '🚶', gym: '🏋️', yoga: '🧘', cycling: '🚴', swimming: '🏊', other: '🏅' }
function exerciseEmoji(type) { return exerciseEmojis[type] || '🏅' }

async function addRecord() {
  if (!form.value.record_date) return
  await api.createHealth(form.value)
  form.value = { record_date: today, exercise_type: '', exercise_minutes: 0, water_ml: 0, steps: 0, weight_kg: 0, note: '' }
  await load()
}

async function deleteRecord(r) {
  if (!confirm(t('confirmDelete'))) return
  await api.deleteHealth(r.id)
  await load()
}

async function load() {
  records.value = await api.getHealth() || []
}

onMounted(load)
</script>

<style scoped>
.health-page { max-width: 800px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.add-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; }
.add-card h3 { font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 12px; }
.form-row { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; flex-wrap: wrap; }
.form-row input, .form-row select { padding: 9px 14px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 13px; background: #fafbfd; }
.form-row label { font-size: 13px; font-weight: 500; color: #6b7085; }
.btn-primary { padding: 10px 20px; background: #4f46e5; color: #fff; border: none; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; }
.water-section { display: flex; align-items: center; gap: 8px; }
.water-section label { font-size: 13px; font-weight: 600; color: #1a1a2e; }
.water-btns { display: flex; gap: 4px; }
.water-btn { padding: 6px 12px; border: 1px solid #bfdbfe; border-radius: 6px; background: #eff6ff; color: #2563eb; cursor: pointer; font-size: 12px; font-weight: 600; }
.water-btn:hover { background: #dbeafe; }
.water-total { font-size: 14px; font-weight: 700; color: #2563eb; }
.water-reset { padding: 4px 10px; border: 1px solid #eef0f4; border-radius: 6px; background: #fff; cursor: pointer; font-size: 11px; color: #8b8fa8; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px; text-align: center; }
.stat-value { font-size: 28px; font-weight: 800; }
.stat-exercise { color: #10b981; }
.stat-water { color: #3b82f6; }
.stat-steps { color: #f59e0b; }
.stat-label { font-size: 12px; color: #8b8fa8; margin-top: 4px; }
.chart-section { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; }
.section-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin-bottom: 14px; }
.water-progress { height: 20px; background: #eff6ff; border-radius: 10px; overflow: hidden; }
.water-fill { height: 100%; background: linear-gradient(90deg, #60a5fa, #3b82f6); border-radius: 10px; transition: width 0.3s; }
.water-label { font-size: 12px; color: #6b7085; margin-top: 6px; text-align: center; }
.record-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f0f1f5; flex-wrap: wrap; }
.record-date { font-size: 13px; font-weight: 600; color: #1a1a2e; min-width: 90px; }
.record-detail { display: flex; gap: 12px; font-size: 13px; color: #6b7085; flex: 1; }
.record-note-inline { font-size: 12px; color: #8b8fa8; }
.btn-del { padding: 4px 12px; border: 1px solid #fecaca; border-radius: 6px; background: #fff; color: #ef4444; cursor: pointer; font-size: 11px; margin-left: auto; }
.empty { color: #b0b4c8; font-size: 13px; padding: 20px 0; text-align: center; }
</style>
