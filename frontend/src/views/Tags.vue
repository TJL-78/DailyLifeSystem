<template>
  <div class="tags-page">
    <h1 class="page-title">{{ t('tagsTitle') }}</h1>

    <div v-if="!tags.length" class="empty">{{ t('noTags') }}</div>

    <div v-for="tag in tags" :key="tag.id" class="tag-card">
      <div class="tag-color-dot" :style="{ background: tag.color || '#4f46e5' }"></div>
      <div class="tag-body">
        <div v-if="tag._editing" class="tag-edit-row">
          <input v-model="tag._editName" class="tag-input" @keypress.enter="saveTag(tag)" />
          <input v-model="tag._editColor" type="color" class="tag-color-input" />
          <button class="btn-primary btn-sm" @click="saveTag(tag)">{{ t('save') }}</button>
          <button class="btn-secondary btn-sm" @click="tag._editing = false">{{ t('cancel') }}</button>
        </div>
        <div v-else class="tag-display">
          <span class="tag-name">#{{ tag.name }}</span>
          <span class="tag-count">{{ tag.usage_count || 0 }} {{ t('tagUsageCount') }}</span>
        </div>
      </div>
      <div class="tag-actions">
        <button v-if="!tag._editing" class="btn-secondary btn-sm" @click="startEdit(tag)">{{ t('renameTag') }}</button>
        <button class="btn-del btn-sm" @click="deleteTag(tag)">{{ t('delete') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from '../i18n'
import api from '../api'

const { t } = useI18n()
const tags = ref([])

async function load() {
  tags.value = (await api.getTags() || []).map(tag => ({
    ...tag, _editing: false, _editName: tag.name, _editColor: tag.color || '#4f46e5'
  }))
}

function startEdit(tag) {
  tag._editing = true
  tag._editName = tag.name
  tag._editColor = tag.color || '#4f46e5'
}

async function saveTag(tag) {
  await api.updateTag(tag.id, { name: tag._editName, color: tag._editColor })
  tag._editing = false
  await load()
}

async function deleteTag(tag) {
  if (!confirm(t('confirmDeleteTag'))) return
  await api.deleteTag(tag.id)
  await load()
}

onMounted(load)
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.tag-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 16px 20px; margin-bottom: 10px; display: flex; align-items: center; gap: 14px; }
.tag-color-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
.tag-body { flex: 1; }
.tag-display { display: flex; align-items: center; gap: 12px; }
.tag-name { font-size: 14px; font-weight: 600; color: #1a1a2e; }
.tag-count { font-size: 12px; color: #8b8fa8; }
.tag-edit-row { display: flex; gap: 8px; align-items: center; }
.tag-input { padding: 7px 12px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 13px; background: #fafbfd; width: 160px; }
.tag-input:focus { outline: none; border-color: #4f46e5; }
.tag-color-input { width: 36px; height: 32px; border: 1px solid #eef0f4; border-radius: 6px; padding: 2px; cursor: pointer; }
.tag-actions { display: flex; gap: 6px; }
.btn-primary { padding: 8px 16px; background: #4f46e5; color: #fff; border: none; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; }
.btn-secondary { padding: 8px 16px; background: #fff; color: #6b7085; border: 1px solid #eef0f4; border-radius: 8px; font-size: 12px; cursor: pointer; }
.btn-sm { padding: 6px 12px; font-size: 11px; }
.btn-del { padding: 6px 12px; border: 1px solid #fecaca; border-radius: 8px; background: #fff; color: #ef4444; cursor: pointer; font-size: 11px; }
.empty { color: #b0b4c8; font-size: 13px; padding: 40px 0; text-align: center; }
</style>
