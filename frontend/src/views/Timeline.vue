<template>
  <div class="timeline-page">
    <h2>{{ t('timelineTitle') }}</h2>
    <div class="date-nav">
      <button @click="prevDay">{{ t('prevDay') }}</button>
      <input type="date" v-model="selectedDate" />
      <button @click="nextDay">{{ t('nextDay') }}</button>
      <button @click="goToday">{{ t('calToday') }}</button>
      <button class="btn-add-block" @click="showBlockForm = !showBlockForm">{{ t('addTimeBlock') }}</button>
    </div>

    <!-- Time Block Form -->
    <div v-if="showBlockForm" class="block-form">
      <input v-model="newBlock.title" :placeholder="t('blockTitlePh')" class="input" />
      <input type="time" v-model="newBlock.start_time" class="input input-time" />
      <span>-</span>
      <input type="time" v-model="newBlock.end_time" class="input input-time" />
      <input type="color" v-model="newBlock.color" class="input-color" />
      <button class="btn-save" @click="addBlock">{{ t('add') }}</button>
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

    <div v-if="!activities.length && !unscheduledActs.length && !timeBlocks.length" class="empty">{{ t('noTimelineActs') }}</div>

    <!-- 24-hour timeline -->
    <div class="timeline-grid" ref="gridRef">
      <div v-for="hour in 24" :key="hour - 1" class="hour-row">
        <div class="hour-label">{{ String(hour - 1).padStart(2, '0') }}:00</div>
        <div class="hour-cell"></div>
      </div>
      <!-- Current time indicator -->
      <div class="current-time-line" :style="{ top: currentTimeTop + 'px' }"></div>
      <!-- Time Blocks (background) -->
      <div v-for="block in timeBlocks" :key="'tb-' + block.id" class="time-block"
        :style="getTimeBlockStyle(block)" @click="showBlockTooltip(block)">
        <span class="block-label">{{ block.title || t('timeBlock') }}</span>
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
        <p v-if="tooltip.act.scheduled_time">{{ tooltip.act.scheduled_time }}</p>
        <p v-if="tooltip.act.duration_minutes">{{ tooltip.act.duration_minutes }} min</p>
        <p v-if="tooltip.act.status">{{ tooltip.act.status }}</p>
        <button @click="tooltip.visible = false">{{ t('cancel') }}</button>
      </div>
    </div>

    <!-- Time Block Tooltip -->
    <div v-if="blockTooltip.visible" class="tooltip-overlay" @click="blockTooltip.visible = false">
      <div class="tooltip-card" @click.stop>
        <h4>{{ blockTooltip.block.title || t('timeBlock') }}</h4>
        <p>{{ blockTooltip.block.start_time }} - {{ blockTooltip.block.end_time }}</p>
        <div class="tooltip-actions">
          <button @click="blockTooltip.visible = false">{{ t('cancel') }}</button>
          <button class="btn-del" @click="deleteBlock(blockTooltip.block.id)">{{ t('delete') }}</button>
        </div>
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
const timeBlocks = ref([])
const currentMinutes = ref(new Date().getHours() * 60 + new Date().getMinutes())
let timer = null

const HOUR_HEIGHT = 60
const showBlockForm = ref(false)
const newBlock = ref({ title: '', start_time: '09:00', end_time: '10:00', color: '#4f46e5' })

const currentTimeTop = computed(() => (currentMinutes.value / 60) * HOUR_HEIGHT)

const scheduledActs = computed(() => activities.value.filter(a => a.scheduled_time))
const unscheduledActs = computed(() => activities.value.filter(a => !a.scheduled_time))

const tooltip = ref({ visible: false, act: {} })
const blockTooltip = ref({ visible: false, block: {} })

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

function getTimeBlockStyle(block) {
  const [sh, sm] = block.start_time.split(':').map(Number)
  const [eh, em] = block.end_time.split(':').map(Number)
  const top = (sh * 60 + sm) / 60 * HOUR_HEIGHT
  const height = ((eh * 60 + em) - (sh * 60 + sm)) / 60 * HOUR_HEIGHT
  return {
    top: top + 'px',
    height: Math.max(height, 20) + 'px',
    background: block.color + '22',
    borderLeft: '3px solid ' + block.color,
    left: '60px',
    right: '8px',
  }
}

function showTooltip(act, e) {
  tooltip.value = { visible: true, act }
}

function showBlockTooltip(block) {
  blockTooltip.value = { visible: true, block }
}

async function addBlock() {
  if (!newBlock.value.start_time || !newBlock.value.end_time) return
  try {
    await api.createTimeBlock({
      block_date: selectedDate.value,
      ...newBlock.value,
    })
    newBlock.value = { title: '', start_time: '09:00', end_time: '10:00', color: '#4f46e5' }
    showBlockForm.value = false
    await loadTimeBlocks()
  } catch (e) { console.error(e) }
}

async function deleteBlock(id) {
  try {
    await api.deleteTimeBlock(id)
    blockTooltip.value.visible = false
    await loadTimeBlocks()
  } catch (e) { console.error(e) }
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

async function loadTimeBlocks() {
  try {
    timeBlocks.value = await api.getTimeBlocks(selectedDate.value) || []
  } catch { timeBlocks.value = [] }
}

watch(selectedDate, () => { loadActivities(); loadTimeBlocks() }, { immediate: true })

onMounted(() => {
  timer = setInterval(() => {
    const now = new Date()
    currentMinutes.value = now.getHours() * 60 + now.getMinutes()
  }, 60000)
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
.date-nav { display: flex; gap: 8px; align-items: center; margin-bottom: 16px; flex-wrap: wrap; }
.date-nav button { padding: 6px 12px; border: 1px solid #ddd; border-radius: 6px; background: #fff; cursor: pointer; }
.date-nav button:hover { background: #f0f0ff; }
.date-nav input { padding: 6px 10px; border: 1px solid #ddd; border-radius: 6px; }
.btn-add-block { background: #4f46e5 !important; color: #fff !important; border-color: #4f46e5 !important; }
.block-form { display: flex; gap: 8px; align-items: center; margin-bottom: 16px; padding: 12px; background: #f9f9fb; border-radius: 8px; flex-wrap: wrap; }
.input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; }
.input-time { width: 110px; }
.input-color { width: 36px; height: 36px; padding: 2px; border: 1px solid #ddd; border-radius: 6px; cursor: pointer; }
.btn-save { padding: 8px 16px; background: #4f46e5; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; }
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
.time-block { position: absolute; border-radius: 6px; padding: 4px 8px; font-size: 11px; overflow: hidden; cursor: pointer; z-index: 2; opacity: 0.8; }
.time-block:hover { opacity: 1; }
.block-label { color: #374151; font-weight: 500; }
.activity-block { position: absolute; border-radius: 6px; padding: 4px 8px; color: #fff; font-size: 12px; overflow: hidden; cursor: pointer; opacity: 0.9; min-height: 20px; z-index: 5; }
.activity-block:hover { opacity: 1; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.block-title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tooltip-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); z-index: 1000; display: flex; align-items: center; justify-content: center; }
.tooltip-card { background: #fff; padding: 24px; border-radius: 12px; min-width: 280px; max-width: 400px; }
.tooltip-card h4 { margin-bottom: 8px; }
.tooltip-card p { margin: 4px 0; font-size: 13px; color: #555; }
.tooltip-actions { display: flex; gap: 8px; margin-top: 12px; }
.tooltip-card button { padding: 6px 16px; border: 1px solid #ddd; border-radius: 6px; background: #fff; cursor: pointer; }
.btn-del { color: #e74c3c !important; border-color: #e74c3c !important; }
</style>
