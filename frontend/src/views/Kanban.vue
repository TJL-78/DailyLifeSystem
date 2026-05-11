<template>
  <div class="kanban-page">
    <h1 class="page-title">{{ t('kanbanTitle') }}</h1>

    <div class="kanban-board">
      <div v-for="col in columns" :key="col.status" class="kanban-column"
        @dragover.prevent @drop="onDrop($event, col.status)">
        <div class="column-header">
          <span class="column-title">{{ t(col.label) }}</span>
          <span class="column-count">{{ getColumnItems(col.status).length }}</span>
        </div>
        <div class="column-body">
          <div v-for="a in getColumnItems(col.status)" :key="a.id"
            class="kanban-card" draggable="true"
            @dragstart="onDragStart($event, a)">
            <div class="card-title">{{ a.title }}</div>
            <div class="card-meta">
              <span class="badge" :class="'badge-' + a.priority">{{ a.priority }}</span>
              <span v-if="a.scheduled_date" class="card-date">{{ a.scheduled_date }}</span>
            </div>
            <div v-if="a.tags && a.tags.length" class="card-tags">
              <span v-for="tag in a.tags" :key="tag" class="badge badge-tag">#{{ tag }}</span>
            </div>
          </div>
          <div v-if="!getColumnItems(col.status).length" class="column-empty">{{ t('noActs') }}</div>
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
const activities = ref([])
const columns = [
  { status: 'pending', label: 'pending' },
  { status: 'in_progress', label: 'inProgress' },
  { status: 'completed', label: 'completed' },
]

let dragItem = null

function getColumnItems(status) {
  return activities.value.filter(a => a.status === status)
}

function onDragStart(e, activity) {
  dragItem = activity
  e.dataTransfer.effectAllowed = 'move'
}

async function onDrop(e, newStatus) {
  if (!dragItem || dragItem.status === newStatus) return
  const item = dragItem
  dragItem = null
  if (newStatus === 'completed') {
    await api.completeActivity(item.id)
  } else if (newStatus === 'in_progress') {
    await api.startActivity(item.id)
  } else if (newStatus === 'pending') {
    await api.cancelActivity(item.id)
  }
  await load()
}

async function load() {
  const res = await api.getActivities({}) || []
  activities.value = Array.isArray(res) ? res : (res.activities || [])
}

onMounted(load)
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.kanban-board { display: flex; gap: 16px; min-height: 70vh; }
.kanban-column { flex: 1; background: #f0f1f5; border-radius: 14px; padding: 16px; min-width: 250px; }
.column-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; padding: 0 4px; }
.column-title { font-size: 14px; font-weight: 700; color: #1a1a2e; }
.column-count { font-size: 12px; font-weight: 600; color: #8b8fa8; background: #fff; padding: 2px 10px; border-radius: 100px; }
.column-body { min-height: 100px; }
.kanban-card { background: #fff; border: 1px solid #eef0f4; border-radius: 10px; padding: 14px 16px; margin-bottom: 8px; cursor: grab; transition: box-shadow 0.2s; }
.kanban-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
.kanban-card:active { cursor: grabbing; }
.card-title { font-size: 13px; font-weight: 600; color: #1a1a2e; margin-bottom: 6px; }
.card-meta { display: flex; gap: 8px; align-items: center; font-size: 11px; color: #8b8fa8; }
.card-date { font-size: 11px; }
.card-tags { margin-top: 6px; display: flex; gap: 4px; flex-wrap: wrap; }
.badge { display: inline-flex; padding: 2px 10px; border-radius: 100px; font-size: 11px; font-weight: 600; }
.badge-low { background: #ecfdf5; color: #059669; }
.badge-medium { background: #fffbeb; color: #d97706; }
.badge-high { background: #fef2f2; color: #dc2626; }
.badge-urgent { background: #dc2626; color: #fff; }
.badge-tag { background: #eef2ff; color: #4f46e5; font-size: 10px; }
.column-empty { color: #b0b4c8; font-size: 12px; text-align: center; padding: 20px 0; }
</style>
