<template>
  <div class="calendar-page">
    <h1 class="page-title">{{ t('calTitle') }}</h1>
    <div class="cal-header">
      <button @click="changeYear(-1)">{{ t('prevYear') }}</button>
      <button @click="changeMonth(-1)">{{ t('prevMonth') }}</button>
      <span class="cal-title">{{ year }}年 {{ month + 1 }}月</span>
      <button @click="changeMonth(1)">{{ t('nextMonth') }}</button>
      <button @click="changeYear(1)">{{ t('nextYear') }}</button>
      <button class="btn-today" @click="goToday">{{ t('calToday') }}</button>
    </div>
    <div class="cal-grid">
      <div class="cal-weekday" v-for="d in weekdays" :key="d">{{ d }}</div>
      <div v-for="(day, i) in calendarDays" :key="i"
        class="cal-day" :class="{ other: day.other, today: day.isToday, selected: day.date === selectedDate }"
        @click="selectDay(day)">
        <span class="day-num">{{ day.day }}</span>
        <div v-if="dayEvents(day.date).length" class="day-dots">
          <span v-for="n in Math.min(dayEvents(day.date).length, 3)" :key="n" class="dot"></span>
        </div>
      </div>
    </div>
    <div v-if="selectedDate" class="day-detail">
      <h3>{{ selectedDate }}{{ t('dayDetail') }}</h3>
      <ul class="activity-list" v-if="dayEvents(selectedDate).length">
        <ActivityItem v-for="a in dayEvents(selectedDate)" :key="a.id" :activity="a"
          @toggle="toggleActivity" @start="startActivity" @cancel="cancelActivity" @delete="deleteActivity" />
      </ul>
      <div v-else class="empty">{{ t('noDayActs') }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from '../i18n'
import api from '../api'
import ActivityItem from '../components/ActivityItem.vue'

const { t } = useI18n()
const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth())
const selectedDate = ref(null)
const events = ref([])
const weekdays = ['日', '一', '二', '三', '四', '五', '六']

const calendarDays = computed(() => {
  const first = new Date(year.value, month.value, 1)
  const lastDay = new Date(year.value, month.value + 1, 0).getDate()
  const startDow = first.getDay()
  const days = []
  const prevLast = new Date(year.value, month.value, 0).getDate()
  for (let i = startDow - 1; i >= 0; i--) {
    const d = prevLast - i
    const m = month.value === 0 ? 12 : month.value
    const y = month.value === 0 ? year.value - 1 : year.value
    days.push({ day: d, date: `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`, other: true, isToday: false })
  }
  const todayStr = new Date().toISOString().slice(0, 10)
  for (let d = 1; d <= lastDay; d++) {
    const date = `${year.value}-${String(month.value + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({ day: d, date, other: false, isToday: date === todayStr })
  }
  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    const m = month.value === 11 ? 1 : month.value + 2
    const y = month.value === 11 ? year.value + 1 : year.value
    days.push({ day: d, date: `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`, other: true, isToday: false })
  }
  return days
})

function dayEvents(date) {
  return events.value.filter(e => e.scheduled_date === date)
}

function changeMonth(d) { month.value += d; if (month.value < 0) { month.value = 11; year.value-- } else if (month.value > 11) { month.value = 0; year.value++ }; loadEvents() }
function changeYear(d) { year.value += d; loadEvents() }
function goToday() { const n = new Date(); year.value = n.getFullYear(); month.value = n.getMonth(); selectedDate.value = n.toISOString().slice(0, 10); loadEvents() }
function selectDay(day) { selectedDate.value = day.date }

async function loadEvents() {
  const start = `${year.value}-${String(month.value + 1).padStart(2, '0')}-01`
  const end = `${year.value}-${String(month.value + 1).padStart(2, '0')}-${new Date(year.value, month.value + 1, 0).getDate()}`
  const res = await api.getCalendarEvents(start, end) || []
  events.value = Array.isArray(res) ? res : (res.events || [])
}

async function toggleActivity(a) { if (a.status !== 'completed') { await api.completeActivity(a.id); await loadEvents() } }
async function startActivity(a) { await api.startActivity(a.id); await loadEvents() }
async function cancelActivity(a) { await api.cancelActivity(a.id); await loadEvents() }
async function deleteActivity(a) { if (!confirm(t('confirmDelete'))) return; await api.deleteActivity(a.id); await loadEvents() }

onMounted(loadEvents)
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.cal-header { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.cal-header button { padding: 8px 14px; border: 1px solid #eef0f4; border-radius: 8px; background: #fff; cursor: pointer; font-size: 13px; font-weight: 500; color: #6b7085; }
.cal-header button:hover { background: #f8f9fc; }
.btn-today { background: #4f46e5 !important; color: #fff !important; border-color: #4f46e5 !important; }
.cal-title { font-size: 16px; font-weight: 700; color: #1a1a2e; margin: 0 8px; }
.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; background: #fff; border: 1px solid #eef0f4; border-radius: 14px; overflow: hidden; }
.cal-weekday { padding: 12px; text-align: center; font-size: 12px; font-weight: 600; color: #8b8fa8; background: #fafbfd; }
.cal-day { padding: 10px; min-height: 70px; cursor: pointer; transition: background 0.15s; position: relative; }
.cal-day:hover { background: #f8f9fc; }
.cal-day.other { color: #d1d5e0; }
.cal-day.today .day-num { background: #4f46e5; color: #fff; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; }
.cal-day.selected { background: #f0f0ff; }
.day-num { font-size: 13px; font-weight: 600; }
.day-dots { display: flex; gap: 3px; margin-top: 4px; }
.dot { width: 5px; height: 5px; border-radius: 50%; background: #4f46e5; }
.day-detail { margin-top: 24px; background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; }
.day-detail h3 { font-size: 15px; font-weight: 700; margin-bottom: 14px; color: #1a1a2e; }
.activity-list { list-style: none; padding: 0; }
.empty { color: #b0b4c8; font-size: 13px; padding: 20px 0; text-align: center; }
</style>
