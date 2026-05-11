<template>
  <div class="timeline-page">
    <h2>{{ t('timelineTitle') }}</h2>
    <div class="date-nav">
      <button @click="prevDay">{{ t('prevDay') }}</button>
      <input type="date" v-model="selectedDate" />
      <button @click="nextDay">{{ t('nextDay') }}</button>
      <button @click="goToday">{{ t('calToday') }}</button>
    </div>

    <!-- Unscheduled activities -->
    <div v-if="unscheduledActs.length" class="unscheduled-section">
      <h3>{{ t('unscheduled') }}</h3>
      <div class="unscheduled-list">
        <div v-for="act in unscheduledActs" :key="act.id" class="unscheduled-item"
          :style="{ borderLeft: '4px solid ' + getCatColor(act.category_id) }"
          @click="showTooltip(act, $event)">
          {{ act.title }}
        </div>
      </div>
    </div>

    <div v-if="!activities.length && !unscheduledActs.length" class="empty">{{ t('noTimelineActs') }}</div>

    <!-- 24-hour timeline -->
    <div class="timeline-grid" ref="gridRef">
      <div v-for="hour in 24" :key="hour - 1" class="hour-row">
        <div class="hour-label">{{ String(hour - 1).padStart(2, '0') }}:00</div>
        <div class="hour-cell"></div>
      </div>
      <!-- Current time indicator -->
      <div class="current-time-line" :style="{ top: currentTimeTop + 'px' }">
        <span class="time-label">{{ t('currentTime') }}</span>
      </div>
      <!-- Activity blocks -->
      <div v-for="act in scheduledActs" :key="act.id" class="activity-block"
        :style="getBlockStyle(act)"
        @click="showTooltip(act, $event)">
        <span class="block-title">{{ act.title }}</span>
      </div>
    </div>

    <!-- Tooltip -->
    <div v-if="tooltip.visible" class="tooltip-overlay" @click="tooltip.visible = false">
      <div class="tooltip-card" @click.stop>
        <h4>{{ tooltip.act.title }}</h4>
        <p v-if="tooltip.act.description">{{ tooltip.act.description }}</p>
        <p v-if="tooltip.act.scheduled_time">⏰ {{ tooltip.act.scheduled_time }}</p>
        <p v-if="tooltip.act.duration_minutes">⏱ {{ tooltip.act.duration_minutes }} min</p>
        <p>{{ tooltip.act.status }}</p>
        <button @click="tooltip.visible = false">{{ t('cancel') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import api from '../api'
import { useAppStore } from '../stores/app'
import { useI18n } from '../i18n'

const store = useAppStore()
const { t } = useI18n()

const today = new Date().toISOString().slice(0, 10)
const selectedDate = ref(today)
const activities = ref([])
const currentMinutes = ref(new Date().getHours() * 60 + new Date().getMinutes())
let timer = null

const HOUR_HEIGHT = 60

const currentTimeTop = computed(() => (currentMinutes.value / 60) * HOUR_HEIGHT)

const scheduledActs = computed(() => activities.value.filter(a => a.scheduled_time))
const unscheduledActs = computed(() => activities.value.filter(a => !a.scheduled_time))

const tooltip = ref({ visible: false, act: {} })

function getCatColor(catId) {
  const cat = store.categories.find(c => c.id === catId)
  return cat ? cat.color : '#95a5a6'
}

function getBlockStyle(act) {
  const [h, m] = act.scheduled_time.split(':').map(Number)
  const top = (h * 60 + m) / 60 * HOUR_HEIGHT
  const duration = act.duration_minutes || 30
  const height = (duration / 60) * HOUR_HEIGHT
  return {
    top: top + 'px',
    height: Math.max(height, 20) + 'px',
    background: getCatColor(act.category_id),
    left: '60px',
    right: '8px',
  }
}

function showTooltip(act, e) {
  tooltip.value = { visible: true, act }
}

function prevDay() {
  const d = new Date(selectedDate.value)
  d.setDate(d.getDate() - 1)
  selectedDate.value = d.toISOString().slice(0, 10)
}
function nextDay() {
  const d = new Date(selectedDate.value)
  d.setDate(d.getDate() + 1)
  selectedDate.value = d.toISOString().slice(0, 10)
}
function goToday() {
  selectedDate.value = new Date().toISOString().slice(0, 10)
}

async function loadActivities() {
  try {
    const data = await api.getCalendarEvents(selectedDate.value, selectedDate.value)
    activities.value = data || []
  } catch { activities.value = [] }
}

watch(selectedDate, loadActivities, { immediate: true })

onMounted(() => {
  timer = setInterval(() => {
    const now = new Date()
    currentMinutes.value = now.getHours() * 60 + now.getMinutes()
  }, 60000)
  // Scroll to 6am
  setTimeout(() => {
    const grid = document.querySelector('.timeline-grid')
    if (grid) grid.scrollTop = 6 * HOUR_HEIGHT
  }, 100)
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.timeline-page { padding: 24px; max-width: 900px; }
h2 { margin-bottom: 16px; }
.date-nav { display: flex; gap: 8px; align-items: center; margin-bottom: 16px; }
.date-nav button { padding: 6px 12px; border: 1px solid #ddd; border-radius: 6px; background: #fff; cursor: pointer; }
.date-nav button:hover { background: #f0f0ff; }
.date-nav input { padding: 6px 10px; border: 1px solid #ddd; border-radius: 6px; }
.unscheduled-section { margin-bottom: 16px; padding: 12px; background: #f9f9fb; border-radius: 8px; }
.unscheduled-section h3 { font-size: 13px; color: #666; margin-bottom: 8px; }
.unscheduled-list { display: flex; flex-wrap: wrap; gap: 8px; }
.unscheduled-item { padding: 6px 12px; background: #fff; border-radius: 6px; font-size: 13px; cursor: pointer; }
.empty { color: #999; padding: 40px; text-align: center; }
.timeline-grid { position: relative; height: 600px; overflow-y: auto; border: 1px solid #eee; border-radius: 8px; background: #fafbfd; }
.hour-row { display: flex; height: 60px; border-bottom: 1px solid #eef0f4; }
.hour-label { width: 60px; padding: 4px 8px; font-size: 11px; color: #999; flex-shrink: 0; }
.hour-cell { flex: 1; background: #f8f9fc; }
.current-time-line { position: absolute; left: 50px; right: 0; height: 2px; background: #e74c3c; z-index: 10; pointer-events: none; }
.current-time-line .time-label { position: absolute; left: -50px; top: -8px; font-size: 10px; color: #e74c3c; }
.activity-block { position: absolute; border-radius: 6px; padding: 4px 8px; color: #fff; font-size: 12px; overflow: hidden; cursor: pointer; opacity: 0.9; min-height: 20px; z-index: 5; }
.activity-block:hover { opacity: 1; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.block-title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tooltip-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); z-index: 1000; display: flex; align-items: center; justify-content: center; }
.tooltip-card { background: #fff; padding: 24px; border-radius: 12px; min-width: 280px; max-width: 400px; }
.tooltip-card h4 { margin-bottom: 8px; }
.tooltip-card p { margin: 4px 0; font-size: 13px; color: #555; }
.tooltip-card button { margin-top: 12px; padding: 6px 16px; border: 1px solid #ddd; border-radius: 6px; background: #fff; cursor: pointer; }
</style>
