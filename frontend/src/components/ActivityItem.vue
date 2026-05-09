<template>
  <li class="activity-item" :class="activity.status">
    <div class="activity-check" :class="{ checked: activity.status === 'completed' }" @click="$emit('toggle', activity)">
      {{ activity.status === 'completed' ? '✓' : '' }}
    </div>
    <div class="activity-body">
      <div class="activity-title">{{ activity.title }}</div>
      <div class="activity-meta">
        <span class="badge" :class="'badge-' + activity.priority">{{ priorityLabel }}</span>
        <span v-if="categoryName" class="badge badge-cat">{{ categoryName }}</span>
        <span v-if="activity.scheduled_date">📅 {{ activity.scheduled_date }}</span>
        <span v-if="activity.duration_minutes">⏱ {{ activity.duration_minutes }}{{ t('minutes') }}</span>
        <span v-for="tag in activity.tags || []" :key="tag" class="badge badge-tag">#{{ tag }}</span>
        <span v-if="activity.parent_id" class="badge badge-sub">{{ t('subtask') }}</span>
      </div>
      <div v-if="showSubtasks && !activity.parent_id" class="subtask-section">
        <div v-for="s in subtasks" :key="s.id" class="subtask-item">
          <div class="subtask-check" :class="{ checked: s.status === 'completed' }" @click="$emit('toggleSub', s)">{{ s.status === 'completed' ? '✓' : '' }}</div>
          <span :style="s.status === 'completed' ? 'text-decoration:line-through;color:#b0b4c8' : ''">{{ s.title }}</span>
          <button class="subtask-del" @click="$emit('deleteSub', s)">✕</button>
        </div>
        <div class="subtask-add">
          <input v-model="newSubtask" :placeholder="t('addSubtaskPlaceholder')" @keypress.enter="addSub" />
          <button @click="addSub">+</button>
        </div>
      </div>
    </div>
    <div class="activity-actions">
      <button v-if="activity.status === 'pending'" @click="$emit('start', activity)">{{ t('start') }}</button>
      <button v-if="activity.status !== 'completed' && activity.status !== 'cancelled'" @click="$emit('cancel', activity)">{{ t('cancel') }}</button>
      <button class="btn-del" @click="$emit('delete', activity)">{{ t('delete') }}</button>
    </div>
  </li>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from '../i18n'
import { useAppStore } from '../stores/app'
import api from '../api'

const props = defineProps({
  activity: Object,
  showSubtasks: { type: Boolean, default: false }
})
const emit = defineEmits(['toggle', 'start', 'cancel', 'delete', 'toggleSub', 'deleteSub', 'addSubtask'])

const { t } = useI18n()
const store = useAppStore()
const subtasks = ref([])
const newSubtask = ref('')

const priorityLabels = { low: 'low', medium: 'medium', high: 'high', urgent: 'urgent' }
const priorityLabel = computed(() => t(priorityLabels[props.activity.priority] || 'medium'))
const categoryName = computed(() => {
  const c = store.categories.find(c => c.id === props.activity.category_id)
  return c ? `${c.icon} ${c.name}` : ''
})

async function loadSubtasks() {
  if (props.showSubtasks && !props.activity.parent_id) {
    subtasks.value = await api.getSubtasks(props.activity.id) || []
  }
}

async function addSub() {
  if (!newSubtask.value.trim()) return
  await api.createSubtask(props.activity.id, { title: newSubtask.value.trim() })
  newSubtask.value = ''
  await loadSubtasks()
}

onMounted(loadSubtasks)
watch(() => props.activity.id, loadSubtasks)
</script>

<style scoped>
.activity-item { background: #fff; border-radius: 12px; padding: 16px 20px; margin-bottom: 8px; display: flex; align-items: flex-start; gap: 14px; border: 1px solid #eef0f4; transition: box-shadow 0.2s; list-style: none; }
.activity-item:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.04); }
.activity-item.completed .activity-title { text-decoration: line-through; color: #b0b4c8; }
.activity-check { width: 20px; height: 20px; border-radius: 50%; border: 2px solid #d1d5e0; cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 11px; margin-top: 2px; transition: all 0.15s; }
.activity-check:hover { border-color: #10b981; }
.activity-check.checked { background: #10b981; border-color: #10b981; color: #fff; }
.activity-body { flex: 1; min-width: 0; }
.activity-title { font-size: 14px; font-weight: 600; color: #1a1a2e; }
.activity-meta { font-size: 12px; color: #8b8fa8; margin-top: 6px; display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.badge { display: inline-flex; padding: 2px 10px; border-radius: 100px; font-size: 11px; font-weight: 600; }
.badge-low { background: #ecfdf5; color: #059669; }
.badge-medium { background: #fffbeb; color: #d97706; }
.badge-high { background: #fef2f2; color: #dc2626; }
.badge-urgent { background: #dc2626; color: #fff; }
.badge-cat { background: #f3f4f6; color: #6b7085; }
.badge-tag { background: #eef2ff; color: #4f46e5; font-size: 10px; }
.badge-sub { background: #f5f3ff; color: #7c3aed; font-size: 10px; }
.activity-actions { display: flex; gap: 4px; flex-shrink: 0; }
.activity-actions button { padding: 6px 12px; border: 1px solid #eef0f4; border-radius: 8px; cursor: pointer; font-size: 11px; background: #fff; color: #6b7085; font-weight: 500; transition: all 0.15s; }
.activity-actions button:hover { background: #f8f9fc; color: #1a1a2e; }
.activity-actions .btn-del { color: #ef4444; border-color: #fecaca; }
.activity-actions .btn-del:hover { background: #fef2f2; }
.subtask-section { margin-top: 10px; padding-left: 34px; }
.subtask-item { display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 13px; }
.subtask-check { width: 16px; height: 16px; border-radius: 50%; border: 2px solid #d1d5e0; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 10px; flex-shrink: 0; transition: all 0.15s; }
.subtask-check.checked { background: #10b981; border-color: #10b981; color: #fff; }
.subtask-del { border: none; background: none; color: #ef4444; cursor: pointer; font-size: 11px; }
.subtask-add { display: flex; gap: 6px; margin-top: 6px; }
.subtask-add input { padding: 7px 12px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 12px; flex: 1; background: #fafbfd; }
.subtask-add input:focus { outline: none; border-color: #4f46e5; background: #fff; }
.subtask-add button { padding: 7px 14px; border: none; background: #4f46e5; color: #fff; border-radius: 8px; cursor: pointer; font-size: 12px; font-weight: 600; }
</style>
