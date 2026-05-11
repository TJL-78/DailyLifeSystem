<template>
  <div class="automation-page">
    <h1 class="page-title">{{ t('automationTitle') }}</h1>

    <!-- Smart Suggestions -->
    <div class="section">
      <h2 class="section-title">{{ t('smartSuggestions') }}</h2>
      <button class="btn-refresh" @click="loadSuggestions">{{ t('refreshSuggestions') }}</button>
      <div v-if="suggestions.length" class="suggestions-grid">
        <div v-for="(s, i) in suggestions" :key="i" class="suggestion-card" :class="'type-' + s.type">
          <span class="suggestion-icon">{{ s.icon }}</span>
          <span class="suggestion-text">{{ currentLang === 'zh' ? s.text : s.text_en }}</span>
        </div>
      </div>
      <div v-else class="empty">{{ t('noSuggestions') }}</div>
    </div>

    <!-- Automation Rules -->
    <div class="section">
      <h2 class="section-title">{{ t('automationRules') }}</h2>
      <div class="rule-form">
        <input v-model="newRule.name" :placeholder="t('ruleNamePh')" class="input" />
        <select v-model="newRule.trigger_type" class="input">
          <option value="pomodoro_count">{{ t('triggerPomodoro') }}</option>
          <option value="activity_complete">{{ t('triggerActivity') }}</option>
        </select>
        <input v-model="newRule.trigger_value" :placeholder="t('triggerValuePh')" class="input input-sm" />
        <select v-model="newRule.action_type" class="input">
          <option value="checkin_habit">{{ t('actionCheckin') }}</option>
          <option value="send_notification">{{ t('actionNotify') }}</option>
        </select>
        <select v-if="newRule.action_type === 'checkin_habit'" v-model="newRule.action_value" class="input">
          <option value="">{{ t('selectHabit') }}</option>
          <option v-for="h in habits" :key="h.id" :value="h.id">{{ h.name }}</option>
        </select>
        <input v-else v-model="newRule.action_value" :placeholder="t('actionValuePh')" class="input" />
        <button class="btn-primary" @click="addRule">{{ t('add') }}</button>
      </div>

      <div v-if="rules.length" class="rules-list">
        <div v-for="rule in rules" :key="rule.id" class="rule-card" :class="{ inactive: !rule.is_active }">
          <div class="rule-info">
            <strong>{{ rule.name }}</strong>
            <span class="rule-desc">
              {{ t('when') }} {{ triggerLabel(rule.trigger_type) }} ≥ {{ rule.trigger_value }}
              → {{ actionLabel(rule.action_type) }}
            </span>
          </div>
          <div class="rule-actions">
            <button class="btn-toggle" @click="toggleRule(rule)">{{ rule.is_active ? t('disable') : t('enable') }}</button>
            <button class="btn-delete" @click="deleteRule(rule.id)">{{ t('delete') }}</button>
          </div>
        </div>
      </div>
      <div v-else class="empty">{{ t('noRules') }}</div>

      <button v-if="rules.length" class="btn-secondary" style="margin-top:12px" @click="checkRules">{{ t('checkRulesNow') }}</button>
      <div v-if="firedResults.length" class="fired-results">
        <div v-for="f in firedResults" :key="f.rule_id" class="fired-item">
          ✅ {{ f.rule_name }}: {{ f.action }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { useI18n } from '../i18n'

const { t, currentLang } = useI18n()
const suggestions = ref([])
const rules = ref([])
const habits = ref([])
const firedResults = ref([])

const newRule = ref({
  name: '',
  trigger_type: 'pomodoro_count',
  trigger_value: '3',
  action_type: 'checkin_habit',
  action_value: '',
})

async function loadSuggestions() {
  try { suggestions.value = await api.getSuggestions() || [] } catch (e) { console.error(e) }
}

async function loadRules() {
  try { rules.value = await api.getAutomationRules() || [] } catch (e) { console.error(e) }
}

async function loadHabits() {
  try { habits.value = await api.getHabits() || [] } catch (e) { console.error(e) }
}

async function addRule() {
  if (!newRule.value.name) return
  try {
    await api.createAutomationRule(newRule.value)
    newRule.value = { name: '', trigger_type: 'pomodoro_count', trigger_value: '3', action_type: 'checkin_habit', action_value: '' }
    await loadRules()
  } catch (e) { console.error(e) }
}

async function toggleRule(rule) {
  try {
    await api.updateAutomationRule(rule.id, { is_active: !rule.is_active })
    await loadRules()
  } catch (e) { console.error(e) }
}

async function deleteRule(id) {
  try { await api.deleteAutomationRule(id); await loadRules() } catch (e) { console.error(e) }
}

async function checkRules() {
  try {
    const res = await api.checkAutomation()
    firedResults.value = res?.fired || []
  } catch (e) { console.error(e) }
}

function triggerLabel(type) {
  const map = { pomodoro_count: t('triggerPomodoro'), activity_complete: t('triggerActivity') }
  return map[type] || type
}

function actionLabel(type) {
  const map = { checkin_habit: t('actionCheckin'), send_notification: t('actionNotify') }
  return map[type] || type
}

onMounted(() => { loadSuggestions(); loadRules(); loadHabits() })
</script>

<style scoped>
.automation-page { max-width: 900px; margin: 0 auto; padding: 24px; }
.page-title { font-size: 22px; font-weight: 700; margin-bottom: 24px; color: var(--text-primary, #1a1a2e); }
.section { margin-bottom: 32px; }
.section-title { font-size: 16px; font-weight: 600; margin-bottom: 12px; color: var(--text-primary, #1a1a2e); }
.btn-refresh { background: #f0f0ff; color: #4f46e5; border: none; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 12px; margin-bottom: 12px; }
.suggestions-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px; }
.suggestion-card { display: flex; align-items: center; gap: 10px; padding: 12px 16px; background: #f8f9fc; border-radius: 8px; font-size: 13px; border-left: 3px solid #4f46e5; }
.suggestion-card.type-overdue { border-left-color: #e74c3c; background: #fef2f2; }
.suggestion-card.type-habit_reminder { border-left-color: #f59e0b; background: #fffbeb; }
.suggestion-card.type-pomodoro_suggest { border-left-color: #4f46e5; }
.suggestion-card.type-break_suggest { border-left-color: #10b981; background: #f0fdf4; }
.suggestion-card.type-evening { border-left-color: #6366f1; background: #eef2ff; }
.suggestion-icon { font-size: 18px; flex-shrink: 0; }
.suggestion-text { color: var(--text-primary, #374151); }
.rule-form { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; align-items: center; }
.input { padding: 8px 12px; border: 1px solid #e2e5f0; border-radius: 6px; font-size: 13px; background: var(--bg-card, #fff); color: var(--text-primary, #1a1a2e); }
.input-sm { width: 60px; }
.btn-primary { background: #4f46e5; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; }
.btn-secondary { background: #f0f0ff; color: #4f46e5; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; }
.rules-list { display: flex; flex-direction: column; gap: 8px; }
.rule-card { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: var(--bg-card, #fff); border: 1px solid #e2e5f0; border-radius: 8px; }
.rule-card.inactive { opacity: 0.5; }
.rule-info { display: flex; flex-direction: column; gap: 4px; }
.rule-info strong { font-size: 14px; color: var(--text-primary, #1a1a2e); }
.rule-desc { font-size: 12px; color: #6b7085; }
.rule-actions { display: flex; gap: 8px; }
.btn-toggle { background: #f0f0ff; color: #4f46e5; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; }
.btn-delete { background: #fef2f2; color: #e74c3c; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; }
.fired-results { margin-top: 12px; }
.fired-item { padding: 8px 12px; background: #f0fdf4; border-radius: 6px; font-size: 13px; color: #065f46; margin-bottom: 6px; }
.empty { color: #a0a4b8; font-size: 13px; padding: 16px 0; }

/* Dark mode */
:root.dark .suggestion-card { background: #1e1e2e !important; border-left-color: #6366f1; }
:root.dark .suggestion-card.type-overdue { background: #2d1b1b !important; }
:root.dark .suggestion-card.type-habit_reminder { background: #2d2a1b !important; }
:root.dark .suggestion-card.type-break_suggest { background: #1b2d1e !important; }
:root.dark .rule-card { background: #1e1e2e !important; border-color: #333 !important; }
:root.dark .input { background: #1e1e2e !important; border-color: #333 !important; color: #e0e0e0 !important; }
:root.dark .fired-item { background: #1b2d1e !important; color: #6ee7b7 !important; }
</style>
