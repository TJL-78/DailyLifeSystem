<template>
  <div class="templates-page">
    <h1 class="page-title">{{ t('templatesTitle') }}</h1>

    <div v-if="!templates.length" class="empty">{{ t('noTemplates') }}</div>

    <div v-for="tmpl in templates" :key="tmpl.id" class="template-card">
      <div class="template-header">
        <div>
          <div class="template-name">{{ tmpl.title }}</div>
          <div class="template-meta">
            <span v-if="tmpl.priority" class="badge" :class="'badge-' + tmpl.priority">{{ tmpl.priority }}</span>
            <span v-if="tmpl.duration_minutes">{{ tmpl.duration_minutes }}min</span>
            <span v-for="tag in (tmpl.tags || [])" :key="tag" class="badge badge-tag">#{{ tag }}</span>
          </div>
        </div>
        <div class="template-actions">
          <button class="btn-primary" @click="useTemplate(tmpl)">{{ t('useTemplate') }}</button>
          <button class="btn-del" @click="deleteTemplate(tmpl)">{{ t('delete') }}</button>
        </div>
      </div>
      <div v-if="tmpl.description" class="template-desc">{{ tmpl.description }}</div>
    </div>

    <div v-if="msg" class="save-msg">{{ msg }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from '../i18n'
import api from '../api'

const { t } = useI18n()
const templates = ref([])
const msg = ref('')

async function load() {
  templates.value = await api.getTemplates() || []
}

async function useTemplate(tmpl) {
  await api.useTemplate(tmpl.id)
  msg.value = t('templateUsed')
  setTimeout(() => msg.value = '', 2000)
}

async function deleteTemplate(tmpl) {
  if (!confirm(t('confirmDeleteTemplate'))) return
  await api.deleteTemplate(tmpl.id)
  await load()
}

onMounted(load)
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.template-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 12px; }
.template-header { display: flex; justify-content: space-between; align-items: flex-start; }
.template-name { font-size: 15px; font-weight: 700; color: #1a1a2e; }
.template-meta { font-size: 12px; color: #8b8fa8; margin-top: 6px; display: flex; gap: 8px; align-items: center; }
.template-desc { font-size: 13px; color: #6b7085; margin-top: 8px; }
.template-actions { display: flex; gap: 6px; }
.btn-primary { padding: 8px 18px; background: #4f46e5; color: #fff; border: none; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; }
.btn-del { padding: 8px 14px; border: 1px solid #fecaca; border-radius: 8px; background: #fff; color: #ef4444; cursor: pointer; font-size: 12px; }
.badge { display: inline-flex; padding: 2px 10px; border-radius: 100px; font-size: 11px; font-weight: 600; }
.badge-low { background: #ecfdf5; color: #059669; }
.badge-medium { background: #fffbeb; color: #d97706; }
.badge-high { background: #fef2f2; color: #dc2626; }
.badge-urgent { background: #dc2626; color: #fff; }
.badge-tag { background: #eef2ff; color: #4f46e5; font-size: 10px; }
.save-msg { margin-top: 10px; color: #10b981; font-size: 13px; font-weight: 600; }
.empty { color: #b0b4c8; font-size: 13px; padding: 40px 0; text-align: center; }
</style>
