<template>
  <div class="categories-page">
    <h1 class="page-title">{{ t('catManage') }}</h1>
    <div class="add-card">
      <div class="form-row">
        <input v-model="form.name" :placeholder="t('catNamePlaceholder')" />
        <input v-model="form.icon" :placeholder="t('iconPlaceholder')" style="width:80px" />
        <input v-model="form.color" type="color" style="width:50px;height:38px;padding:2px;border-radius:8px" />
        <button class="btn-primary" @click="addCategory">{{ t('add') }}</button>
      </div>
    </div>
    <div v-if="!store.categories.length" class="empty">{{ t('noCats') }}</div>
    <ul class="cat-list" v-else>
      <li v-for="c in store.categories" :key="c.id" class="cat-item">
        <span class="cat-dot" :style="{ background: c.color }"></span>
        <span class="cat-icon">{{ c.icon }}</span>
        <span class="cat-name">{{ c.name }}</span>
        <button class="btn-del" @click="deleteCategory(c)">{{ t('delete') }}</button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from '../i18n'
import { useAppStore } from '../stores/app'
import api from '../api'

const { t } = useI18n()
const store = useAppStore()
const form = ref({ name: '', icon: '📁', color: '#4f46e5' })

async function addCategory() {
  if (!form.value.name.trim()) return
  await api.createCategory(form.value)
  form.value = { name: '', icon: '📁', color: '#4f46e5' }
  await store.loadCategories()
}

async function deleteCategory(c) {
  if (!confirm(t('confirmDeleteCat'))) return
  await api.deleteCategory(c.id)
  await store.loadCategories()
}
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.add-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; }
.form-row { display: flex; gap: 8px; align-items: center; }
.form-row input { padding: 9px 14px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 13px; background: #fafbfd; }
.form-row input:focus { outline: none; border-color: #4f46e5; background: #fff; }
.btn-primary { padding: 10px 20px; background: #4f46e5; color: #fff; border: none; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; }
.cat-list { list-style: none; padding: 0; }
.cat-item { background: #fff; border: 1px solid #eef0f4; border-radius: 12px; padding: 14px 20px; margin-bottom: 8px; display: flex; align-items: center; gap: 12px; }
.cat-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.cat-icon { font-size: 18px; }
.cat-name { flex: 1; font-size: 14px; font-weight: 600; color: #1a1a2e; }
.btn-del { padding: 6px 14px; border: 1px solid #fecaca; border-radius: 8px; background: #fff; color: #ef4444; cursor: pointer; font-size: 12px; font-weight: 500; }
.btn-del:hover { background: #fef2f2; }
.empty { color: #b0b4c8; font-size: 13px; padding: 40px 0; text-align: center; }
</style>
