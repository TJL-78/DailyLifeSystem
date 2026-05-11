<template>
  <div class="pomodoro-page">
    <h1 class="page-title">{{ t('pomodoroTitle') }}</h1>

    <div class="timer-card" :class="{ 'break-mode': breakMode }">
      <div v-if="breakMode" class="break-label">{{ t('breakTime') }}</div>
      <div class="timer-ring">
        <svg viewBox="0 0 200 200" class="timer-svg">
          <circle cx="100" cy="100" r="90" fill="none" stroke="#eef0f4" stroke-width="6" />
          <circle cx="100" cy="100" r="90" fill="none" :stroke="breakMode ? '#10b981' : '#4f46e5'" stroke-width="6"
            stroke-linecap="round" :stroke-dasharray="circumference"
            :stroke-dashoffset="dashOffset" class="timer-progress" />
        </svg>
        <div class="timer-digits">
          <span class="time-display" :class="{ 'break-text': breakMode }">{{ displayMinutes }}:{{ displaySeconds }}</span>
        </div>
      </div>

      <div class="duration-options">
        <button v-for="d in durations" :key="d" :class="{ active: selectedDuration === d && !breakMode }"
          @click="selectDuration(d)" :disabled="running">{{ d }}min</button>
        <div class="custom-duration">
          <input type="number" v-model.number="customDuration" :placeholder="t('customDuration')"
            min="1" max="120" :disabled="running" @keypress.enter="applyCustomDuration" class="custom-input" />
          <button @click="applyCustomDuration" :disabled="running" class="custom-btn">OK</button>
        </div>
      </div>

      <div class="form-row" style="justify-content:center;margin:16px 0">
        <select v-model="selectedActivity" class="activity-select">
          <option value="">{{ t('noActivity') }}</option>
          <option v-for="a in activities" :key="a.id" :value="a.id">{{ a.title }}</option>
        </select>
        <select v-model="soundOption" class="sound-select" @change="saveSoundPref">
          <option value="short">{{ t('soundShort') }}</option>
          <option value="long">{{ t('soundLong') }}</option>
          <option value="melody">{{ t('soundMelody') }}</option>
        </select>
      </div>

      <div class="focus-toggle" style="text-align:center;margin-bottom:12px">
        <label class="toggle-label">
          <input type="checkbox" v-model="focusMode" :disabled="running" />
          <span>{{ t('focusModeLabel') }}</span>
        </label>
      </div>

      <div class="timer-controls">
        <template v-if="!showBreakPrompt">
          <button class="btn-primary btn-lg" v-if="!running" @click="startTimer">{{ t('startTimer') }}</button>
          <button class="btn-primary btn-lg" v-else @click="pauseTimer">{{ t('pauseTimer') }}</button>
          <button class="btn-secondary btn-lg" @click="resetTimer">{{ t('resetTimer') }}</button>
        </template>
        <template v-else>
          <button class="btn-break btn-lg" @click="startBreak">{{ t('startBreak') }}</button>
          <button class="btn-secondary btn-lg" @click="skipBreak">{{ t('skipBreak') }}</button>
        </template>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ todayStats.count || 0 }}</div>
        <div class="stat-label">{{ t('sessions') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ todayStats.total_minutes || 0 }}</div>
        <div class="stat-label">{{ t('totalMinutes') }}</div>
      </div>
    </div>

    <div class="history-section">
      <h2 class="section-title">{{ t('pomodoroHistory') }}</h2>
      <div v-if="!todaySessions.length" class="empty">{{ t('noData') }}</div>
      <div v-for="s in todaySessions" :key="s.id" class="session-item">
        <span class="session-time">{{ s.started_at?.slice(11, 16) }} - {{ s.completed_at?.slice(11, 16) }}</span>
        <span class="session-dur">{{ s.duration_minutes }}min</span>
        <span v-if="s.activity_title" class="badge badge-tag">{{ s.activity_title }}</span>
      </div>
    </div>

    <!-- Focus Mode Overlay -->
    <div v-if="focusMode && running" class="focus-overlay">
      <div class="focus-content">
        <div class="focus-timer-display" :class="{ 'break-text': breakMode }">{{ displayMinutes }}:{{ displaySeconds }}</div>
        <p class="focus-msg">{{ t('focusModeMsg') }}</p>
        <button class="btn-exit-focus" @click="pauseTimer">{{ t('exitFocus') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from '../i18n'
import api from '../api'

const { t } = useI18n()
const durations = [15, 25, 45, 60]
const selectedDuration = ref(25)
const customDuration = ref(null)
const selectedActivity = ref('')
const remaining = ref(25 * 60)
const running = ref(false)
const breakMode = ref(false)
const showBreakPrompt = ref(false)
const soundOption = ref(localStorage.getItem('pomodoroSound') || 'short')
const focusMode = ref(false)
const activities = ref([])
const todaySessions = ref([])
const todayStats = ref({})
let timer = null
const circumference = 2 * Math.PI * 90

const dashOffset = computed(() => {
  const total = selectedDuration.value * 60
  const pct = remaining.value / total
  return circumference * (1 - pct)
})
const displayMinutes = computed(() => String(Math.floor(remaining.value / 60)).padStart(2, '0'))
const displaySeconds = computed(() => String(remaining.value % 60).padStart(2, '0'))

function saveSoundPref() {
  localStorage.setItem('pomodoroSound', soundOption.value)
}

function selectDuration(d) {
  breakMode.value = false
  showBreakPrompt.value = false
  selectedDuration.value = d
  remaining.value = d * 60
}

function applyCustomDuration() {
  const d = parseInt(customDuration.value)
  if (d && d > 0 && d <= 120) {
    selectDuration(d)
  }
}

function startTimer() {
  running.value = true
  timer = setInterval(() => {
    if (remaining.value <= 0) {
      clearInterval(timer)
      running.value = false
      if (breakMode.value) {
        breakComplete()
      } else {
        completeSession()
      }
      return
    }
    remaining.value--
  }, 1000)
}

function pauseTimer() {
  clearInterval(timer)
  running.value = false
}

function resetTimer() {
  clearInterval(timer)
  running.value = false
  breakMode.value = false
  showBreakPrompt.value = false
  remaining.value = selectedDuration.value * 60
}

function playBeep() {
  try {
    const ctx = new AudioContext()
    const gain = ctx.createGain()
    gain.connect(ctx.destination)
    gain.gain.value = 0.3

    if (soundOption.value === 'short') {
      const osc = ctx.createOscillator()
      osc.connect(gain)
      osc.frequency.value = 800
      osc.start()
      osc.stop(ctx.currentTime + 0.3)
    } else if (soundOption.value === 'long') {
      const osc = ctx.createOscillator()
      osc.connect(gain)
      osc.frequency.value = 600
      osc.start()
      osc.stop(ctx.currentTime + 1.0)
    } else {
      // melody: three ascending tones
      const freqs = [523, 659, 784]
      freqs.forEach((f, i) => {
        const osc = ctx.createOscillator()
        osc.connect(gain)
        osc.frequency.value = f
        osc.start(ctx.currentTime + i * 0.25)
        osc.stop(ctx.currentTime + i * 0.25 + 0.2)
      })
    }
  } catch (e) { /* ignore */ }
}

function sendNotification(msg) {
  if (Notification.permission === 'granted') {
    new Notification(t('pomodoroTitle'), { body: msg })
  }
}

async function completeSession() {
  playBeep()
  sendNotification(t('sessionComplete'))
  await api.createPomodoroSession({
    duration_minutes: selectedDuration.value,
    activity_id: selectedActivity.value || undefined,
    status: 'completed'
  })
  await loadData()
  // Show break prompt
  showBreakPrompt.value = true
}

function startBreak() {
  showBreakPrompt.value = false
  breakMode.value = true
  selectedDuration.value = 5
  remaining.value = 5 * 60
  startTimer()
}

function skipBreak() {
  showBreakPrompt.value = false
  breakMode.value = false
  selectedDuration.value = 25
  remaining.value = 25 * 60
}

function breakComplete() {
  playBeep()
  sendNotification(t('breakComplete'))
  breakMode.value = false
  showBreakPrompt.value = false
  selectedDuration.value = 25
  remaining.value = 25 * 60
}

async function loadData() {
  const today = new Date().toISOString().slice(0, 10)
  const res = await api.getActivities({ status: 'pending' }) || []
  activities.value = Array.isArray(res) ? res : (res.activities || [])
  todaySessions.value = await api.getPomodoroSessions({ date: today }) || []
  todayStats.value = await api.getPomodoroStats(today) || {}
}

onMounted(() => {
  // Request notification permission
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
  loadData()
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.section-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin-bottom: 14px; }
.timer-card { background: #fff; border: 1px solid #eef0f4; border-radius: 16px; padding: 40px; text-align: center; margin-bottom: 24px; transition: border-color 0.3s; }
.timer-card.break-mode { border-color: #10b981; }
.break-label { font-size: 16px; font-weight: 700; color: #10b981; margin-bottom: 12px; }
.timer-ring { position: relative; width: 220px; height: 220px; margin: 0 auto 24px; }
.timer-svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.timer-progress { transition: stroke-dashoffset 0.5s linear; }
.timer-digits { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); }
.time-display { font-size: 48px; font-weight: 800; color: #4f46e5; font-variant-numeric: tabular-nums; }
.time-display.break-text { color: #10b981; }
.duration-options { display: flex; gap: 8px; justify-content: center; align-items: center; margin-bottom: 16px; flex-wrap: wrap; }
.duration-options button { padding: 8px 18px; border: 1px solid #eef0f4; border-radius: 8px; background: #fff; cursor: pointer; font-size: 13px; font-weight: 500; color: #6b7085; }
.duration-options button.active { background: #4f46e5; color: #fff; border-color: #4f46e5; }
.duration-options button:disabled { opacity: 0.5; cursor: not-allowed; }
.custom-duration { display: flex; gap: 4px; align-items: center; }
.custom-input { width: 70px; padding: 8px 10px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 13px; text-align: center; background: #fafbfd; }
.custom-input:focus { outline: none; border-color: #4f46e5; background: #fff; }
.custom-btn { padding: 8px 12px; border: 1px solid #4f46e5; border-radius: 8px; background: #4f46e5; color: #fff; cursor: pointer; font-size: 13px; font-weight: 600; }
.custom-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.activity-select { padding: 9px 14px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 13px; background: #fafbfd; min-width: 200px; }
.sound-select { padding: 9px 14px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 13px; background: #fafbfd; min-width: 120px; }
.timer-controls { display: flex; gap: 8px; justify-content: center; }
.btn-primary { padding: 10px 24px; background: #4f46e5; color: #fff; border: none; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; }
.btn-secondary { padding: 10px 24px; background: #fff; color: #6b7085; border: 1px solid #eef0f4; border-radius: 10px; font-size: 13px; cursor: pointer; }
.btn-break { padding: 10px 24px; background: #10b981; color: #fff; border: none; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; }
.btn-lg { padding: 12px 32px; font-size: 14px; }
.stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 24px; text-align: center; }
.stat-value { font-size: 32px; font-weight: 800; color: #4f46e5; }
.stat-label { font-size: 12px; color: #8b8fa8; margin-top: 4px; font-weight: 500; }
.history-section { background: #fff; border: 1px solid #eef0f4; border-radius: 16px; padding: 24px 28px; }
.session-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f0f1f5; font-size: 13px; }
.session-time { font-weight: 600; color: #1a1a2e; }
.session-dur { color: #8b8fa8; }
.badge-tag { display: inline-flex; padding: 2px 10px; border-radius: 100px; font-size: 11px; font-weight: 600; background: #eef2ff; color: #4f46e5; }
.empty { color: #b0b4c8; font-size: 13px; padding: 20px 0; text-align: center; }
.form-row { display: flex; gap: 8px; }
.focus-toggle { font-size: 13px; color: #6b7085; }
.toggle-label { display: inline-flex; align-items: center; gap: 6px; cursor: pointer; }
.toggle-label input { accent-color: #4f46e5; }
.focus-overlay { position: fixed; inset: 0; background: rgba(10, 10, 30, 0.95); z-index: 9999; display: flex; align-items: center; justify-content: center; }
.focus-content { text-align: center; }
.focus-timer-display { font-size: 120px; font-weight: 900; color: #4f46e5; font-variant-numeric: tabular-nums; }
.focus-timer-display.break-text { color: #10b981; }
.focus-msg { color: #8b8fa8; font-size: 16px; margin: 24px 0; }
.btn-exit-focus { background: rgba(255,255,255,0.1); color: #aaa; border: 1px solid #555; padding: 10px 24px; border-radius: 8px; cursor: pointer; font-size: 13px; }
.btn-exit-focus:hover { background: rgba(255,255,255,0.2); color: #fff; }
</style>
