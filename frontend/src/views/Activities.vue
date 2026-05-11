<template>
  <div class="activities-page">
    <h1 class="page-title">{{ t('actTitle') }}</h1>

    <div class="search-bar">
      <input v-model="searchQuery" :placeholder="t('searchPlaceholder')" @keypress.enter="doSearch" />
      <button class="btn-primary" @click="doSearch">{{ t('search') }}</button>
      <button class="btn-secondary" @click="clearSearch">{{ t('clear') }}</button>
    </div>

    <div class="add-card" v-if="showAdd">
      <h3>{{ t('addActivity') }}</h3>
      <div class="form-row">
        <input v-model="form.title" :placeholder="t('titlePlaceholder')" class="input-main" />
        <select v-model="form.priority">
          <option value="low">{{ t('low') }}</option>
          <option value="medium">{{ t('medium') }}</option>
          <option value="high">{{ t('high') }}</option>
          <option value="urgent">{{ t('urgent') }}</option>
        </select>
        <select v-model="form.category_id">
          <option value="">{{ t('noCategory') }}</option>
          <option v-for="c in store.categories" :key="c.id" :value="c.id">{{ c.icon }} {{ c.name }}</option>
        </select>
      </div>
      <div class="form-row">
        <input v-model="form.description" :placeholder="t('descPlaceholder')" />
        <input v-model.number="form.duration_minutes" type="number" :placeholder="t('durationPlaceholder')" style="width:120px" />
        <input v-model="form.scheduled_date" type="date" />
      </div>
      <div class="form-row">
        <select v-model="form.repeat">
          <option value="">{{ t('noRepeat') }}</option>
          <option value="daily">{{ t('daily') }}</option>
          <option value="weekly">{{ t('weekly') }}</option>
          <option value="monthly">{{ t('monthly') }}</option>
        </select>
        <input v-model="form.tagsStr" :placeholder="t('tagsPlaceholder')" />
        <button class="btn-primary" @click="addActivity">{{ t('add') }}</button>
      </div>
    </div>
    <button v-else class="btn-primary toggle-add" @click="showAdd = true">+ {{ t('addActivity') }}</button>

    <div class="filter-bar">
      <select v-model="filterStatus">
        <option value="">{{ t('allStatus') }}</option>
        <option value="pending">{{ t('pending') }}</option>
        <option value="in_progress">{{ t('inProgress') }}</option>
        <option value="completed">{{ t('completed') }}</option>
      </select>
      <select v-model="filterPriority">
        <option value="">{{ t('allPriority') }}</option>
        <option value="low">{{ t('low') }}</option>
        <option value="medium">{{ t('medium') }}</option>
        <option value="high">{{ t('high') }}</option>
        <option value="urgent">{{ t('urgent') }}</option>
      </select>
      <select v-model="filterCategory">
        <option value="">{{ t('allCategory') }}</option>
        <option v-for="c in store.categories" :key="c.id" :value="c.id">{{ c.icon }} {{ c.name }}</option>
      </select>
    </div>

    <ul class="activity-list" v-if="filteredActivities.length">
      <ActivityItem v-for="a in filteredActivities" :key="a.id" :activity="a" :showSubtasks="true"
        @toggle="toggleActivity" @start="startActivity" @cancel="cancelActivity" @delete="deleteActivity"
        @saveTemplate="saveAsTemplate" />
    </ul>
    <div v-else class="empty">{{ t('noMatch') }}</div>

    <div v-if="templateMsg" class="save-msg">{{ templateMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from '../i18n'
import { useAppStore } from '../stores/app'
import api from '../api'
import ActivityItem from '../components/ActivityItem.vue'

const { t } = useI18n()
const store = useAppStore()
const activities = ref([])
const searchQuery = ref('')
const showAdd = ref(false)
const filterStatus = ref('')
const filterPriority = ref('')
const filterCategory = ref('')
const form = ref({ title: '', priority: 'medium', category_id: '', description: '', duration_minutes: null, scheduled_date: '', repeat: '', tagsStr: '' })
const templateMsg = ref('')

const filteredActivities = computed(() => {
  return activities.value.filter(a => {
    if (filterStatus.value && a.status !== filterStatus.value) return false
    if (filterPriority.value && a.priority !== filterPriority.value) return false
    if (filterCategory.value && a.category_id !== filterCategory.value) return false
    return true
  })
})

async function load() {
  const res = await api.getActivities({}) || []
  activities.value = Array.isArray(res) ? res : (res.activities || [])
}

async function doSearch() {
  if (!searchQuery.value.trim()) { await load(); return }
  const res = await api.searchActivities(searchQuery.value)
  activities.value = Array.isArray(res) ? res : (res?.activities || [])
}

function clearSearch() { searchQuery.value = ''; load() }

async function addActivity() {
  if (!form.value.title.trim()) return
  const data = { ...form.value }
  if (data.tagsStr) { data.tags = data.tagsStr.split(',').map(s => s.trim()).filter(Boolean) }
  delete data.tagsStr
  if (!data.category_id) delete data.category_id
  if (!data.duration_minutes) delete data.duration_minutes
  if (!data.scheduled_date) delete data.scheduled_date
  if (!data.repeat) delete data.repeat
  if (!data.description) delete data.description
  await api.createActivity(data)
  form.value = { title: '', priority: 'medium', category_id: '', description: '', duration_minutes: null, scheduled_date: '', repeat: '', tagsStr: '' }
  await load()
}

async function toggleActivity(a) { if (a.status !== 'completed') { await api.completeActivity(a.id); await load() } }
async function startActivity(a) { await api.startActivity(a.id); await load() }
async function cancelActivity(a) { await api.cancelActivity(a.id); await load() }
async function deleteActivity(a) { if (!confirm(t('confirmDelete'))) return; await api.deleteActivity(a.id); await load() }

async function saveAsTemplate(a) {
  try {
    await api.createTemplate({
      title: a.title || '',
      description: a.description || '',
      priority: a.priority || 'medium',
      category_id: a.category_id || null,
      duration_minutes: a.duration_minutes || null,
      tags: a.tags || [],
    })
    templateMsg.value = t('templateSaved')
    setTimeout(() => templateMsg.value = '', 2000)
  } catch (e) {
    templateMsg.value = t('templateSaveFailed') || 'Failed to save template'
    setTimeout(() => templateMsg.value = '', 2000)
  }
}

onMounted(load)
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.search-bar { display: flex; gap: 8px; margin-bottom: 16px; }
.search-bar input { flex: 1; padding: 10px 16px; border: 1px solid #eef0f4; border-radius: 10px; font-size: 13px; background: #fff; }
.search-bar input:focus { outline: none; border-color: #4f46e5; }
.btn-primary { padding: 10px 20px; background: #4f46e5; color: #fff; border: none; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; }
.btn-primary:hover { background: #4338ca; }
.btn-secondary { padding: 10px 20px; background: #fff; color: #6b7085; border: 1px solid #eef0f4; border-radius: 10px; font-size: 13px; font-weight: 500; cursor: pointer; }
.add-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 16px; }
.add-card h3 { font-size: 14px; font-weight: 700; margin-bottom: 12px; color: #1a1a2e; }
.form-row { display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
.form-row input, .form-row select { padding: 9px 14px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 12px; background: #fafbfd; }
.form-row input:focus, .form-row select:focus { outline: none; border-color: #4f46e5; background: #fff; }
.input-main { flex: 1; min-width: 200px; }
.form-row select { min-width: 100px; }
.toggle-add { margin-bottom: 16px; }
.filter-bar { display: flex; gap: 8px; margin-bottom: 16px; }
.filter-bar select { padding: 8px 14px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 12px; background: #fff; }
.activity-list { list-style: none; padding: 0; }
.empty { color: #b0b4c8; font-size: 13px; padding: 40px 0; text-align: center; }
.save-msg { margin-top: 10px; color: #10b981; font-size: 13px; font-weight: 600; }
</style>
