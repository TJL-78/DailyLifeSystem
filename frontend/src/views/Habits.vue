<template>
  <div class="habits-page">
    <h1 class="page-title">{{ t('habitsTitle') }}</h1>
    <div class="add-card">
      <div class="form-row">
        <input v-model="form.name" :placeholder="t('habitNamePlaceholder')" class="input-main" />
        <input v-model="form.description" :placeholder="t('habitDescPlaceholder')" />
        <button class="btn-primary" @click="addHabit">{{ t('addHabit') }}</button>
      </div>
    </div>
    <div v-if="!habits.length" class="empty">{{ t('noHabits') }}</div>
    <div v-for="h in habits" :key="h.id" class="habit-card">
      <div class="habit-header">
        <div>
          <div class="habit-name">{{ h.name }}</div>
          <div v-if="h.description" class="habit-desc">{{ h.description }}</div>
        </div>
        <div class="habit-actions">
          <span class="streak">🔥 {{ h.current_streak || 0 }}</span>
          <button class="btn-del" @click="deleteHabit(h)">{{ t('delete') }}</button>
        </div>
      </div>
      <div class="habit-grid">
        <div class="grid-labels">
          <span>{{ t('daysAgo30') }}</span>
          <span>{{ t('today') }}</span>
        </div>
        <div class="grid-row">
          <div v-for="day in getDays(h)" :key="day.date"
            class="grid-cell" :class="{ checked: day.checked, future: day.future }"
            :title="day.date"
            @click="!day.future && toggleCheckin(h, day)">
          </div>
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
const habits = ref([])
const records = ref({})
const form = ref({ name: '', description: '' })

function dateStr(d) { return d.toISOString().slice(0, 10) }

function getDays(habit) {
  const days = []
  const today = new Date()
  for (let i = 29; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const ds = dateStr(d)
    const recs = records.value[habit.id] || []
    days.push({ date: ds, checked: recs.includes(ds), future: false })
  }
  return days
}

async function load() {
  habits.value = await api.getHabits() || []
  const today = new Date()
  const start = new Date(today)
  start.setDate(start.getDate() - 30)
  for (const h of habits.value) {
    const recs = await api.getHabitRecords(h.id, dateStr(start), dateStr(today)) || []
    const dates = Array.isArray(recs) ? recs.map(r => r.record_date || r.date || r) : []
    records.value[h.id] = dates
    h.current_streak = dates.length
  }
}

async function addHabit() {
  if (!form.value.name.trim()) return
  await api.createHabit(form.value)
  form.value = { name: '', description: '' }
  await load()
}

async function deleteHabit(h) {
  if (!confirm(t('confirmDeleteHabit'))) return
  await api.deleteHabit(h.id)
  await load()
}

async function toggleCheckin(habit, day) {
  if (day.checked) {
    await api.uncheckinHabit(habit.id, day.date)
  } else {
    await api.checkinHabit(habit.id, day.date)
  }
  await load()
}

onMounted(load)
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.add-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; }
.form-row { display: flex; gap: 8px; align-items: center; }
.form-row input { padding: 9px 14px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 13px; background: #fafbfd; flex: 1; }
.form-row input:focus { outline: none; border-color: #4f46e5; background: #fff; }
.input-main { flex: 2 !important; }
.btn-primary { padding: 10px 20px; background: #4f46e5; color: #fff; border: none; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; white-space: nowrap; }
.habit-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 12px; }
.habit-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; }
.habit-name { font-size: 15px; font-weight: 700; color: #1a1a2e; }
.habit-desc { font-size: 12px; color: #8b8fa8; margin-top: 2px; }
.habit-actions { display: flex; align-items: center; gap: 10px; }
.streak { font-size: 14px; font-weight: 700; color: #f59e0b; }
.btn-del { padding: 6px 14px; border: 1px solid #fecaca; border-radius: 8px; background: #fff; color: #ef4444; cursor: pointer; font-size: 12px; }
.habit-grid { }
.grid-labels { display: flex; justify-content: space-between; font-size: 10px; color: #b0b4c8; margin-bottom: 4px; }
.grid-row { display: flex; gap: 3px; }
.grid-cell { width: 100%; aspect-ratio: 1; border-radius: 4px; background: #f0f1f5; cursor: pointer; transition: all 0.15s; flex: 1; max-width: 28px; }
.grid-cell:hover { background: #d1d5e0; }
.grid-cell.checked { background: #10b981; }
.grid-cell.future { opacity: 0.3; cursor: default; }
.empty { color: #b0b4c8; font-size: 13px; padding: 40px 0; text-align: center; }
</style>
