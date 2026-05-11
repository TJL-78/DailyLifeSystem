<template>
  <div class="finance-page">
    <h1 class="page-title">{{ t('financeTitle') }}</h1>

    <div class="add-card">
      <h3>{{ t('addFinanceRecord') }}</h3>
      <div class="form-row">
        <input type="date" v-model="form.record_date" />
        <div class="type-toggle">
          <button :class="{ active: form.record_type === 'expense' }" @click="form.record_type = 'expense'">{{ t('expense') }}</button>
          <button :class="{ active: form.record_type === 'income' }" @click="form.record_type = 'income'">{{ t('income') }}</button>
        </div>
        <input type="number" v-model.number="form.amount" :placeholder="t('amountPlaceholder')" min="0" step="0.01" style="width:120px" />
      </div>
      <div class="form-row">
        <select v-model="form.category">
          <option value="">{{ t('financeCategory') }}</option>
          <option v-for="c in (form.record_type === 'expense' ? expenseCats : incomeCats)" :key="c.value" :value="c.value">{{ c.label }}</option>
        </select>
        <input v-model="form.note" :placeholder="t('notePlaceholder')" style="flex:1" />
        <button class="btn-primary" @click="addRecord">{{ t('add') }}</button>
      </div>
    </div>

    <!-- Summary -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value stat-income">+{{ summary.total_income?.toFixed(2) || '0.00' }}</div>
        <div class="stat-label">{{ t('totalIncome') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value stat-expense">-{{ summary.total_expense?.toFixed(2) || '0.00' }}</div>
        <div class="stat-label">{{ t('totalExpense') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" :class="(summary.balance || 0) >= 0 ? 'stat-income' : 'stat-expense'">
          {{ (summary.balance || 0) >= 0 ? '+' : '' }}{{ summary.balance?.toFixed(2) || '0.00' }}
        </div>
        <div class="stat-label">{{ t('balance') }}</div>
      </div>
    </div>

    <!-- Category breakdown -->
    <div class="chart-section" v-if="Object.keys(summary.by_category || {}).length">
      <h2 class="section-title">{{ t('expenseByCategory') }}</h2>
      <div class="cat-bars">
        <div v-for="(val, key) in summary.by_category" :key="key" class="cat-bar-row">
          <span class="cat-bar-label">{{ key }}</span>
          <div class="cat-bar-track">
            <div class="cat-bar-fill" :style="{ width: catPct(val) + '%' }"></div>
          </div>
          <span class="cat-bar-value">¥{{ val.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <!-- Records -->
    <div class="chart-section">
      <h2 class="section-title">{{ t('financeHistory') }}</h2>
      <div v-if="!records.length" class="empty">{{ t('noFinanceRecords') }}</div>
      <div v-for="r in records" :key="r.id" class="record-item">
        <div class="record-date">{{ r.record_date }}</div>
        <span class="type-badge" :class="'type-' + r.record_type">{{ r.record_type === 'income' ? '+' : '-' }}</span>
        <span class="amount" :class="'amount-' + r.record_type">¥{{ r.amount.toFixed(2) }}</span>
        <span class="cat-tag" v-if="r.category">{{ r.category }}</span>
        <span v-if="r.note" class="record-note-inline">{{ r.note }}</span>
        <button class="btn-del" @click="deleteRecord(r)">{{ t('delete') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from '../i18n'
import api from '../api'

const { t } = useI18n()
const today = new Date().toISOString().slice(0, 10)
const form = ref({ record_date: today, record_type: 'expense', amount: 0, category: '', note: '' })
const records = ref([])
const summary = ref({})

const expenseCats = [
  { value: '餐饮', label: '🍽️ 餐饮' }, { value: '交通', label: '🚗 交通' },
  { value: '购物', label: '🛍️ 购物' }, { value: '娱乐', label: '🎮 娱乐' },
  { value: '住房', label: '🏠 住房' }, { value: '医疗', label: '🏥 医疗' },
  { value: '教育', label: '📚 教育' }, { value: '其他', label: '📦 其他' },
]
const incomeCats = [
  { value: '工资', label: '💰 工资' }, { value: '奖金', label: '🎁 奖金' },
  { value: '投资', label: '📈 投资' }, { value: '其他', label: '📦 其他' },
]

const maxCatVal = computed(() => Math.max(...Object.values(summary.value.by_category || { x: 1 }), 1))
function catPct(val) { return (val / maxCatVal.value) * 100 }

async function addRecord() {
  if (!form.value.record_date || !form.value.amount) return
  await api.createFinance(form.value)
  form.value = { record_date: today, record_type: 'expense', amount: 0, category: '', note: '' }
  await load()
}

async function deleteRecord(r) {
  if (!confirm(t('confirmDelete'))) return
  await api.deleteFinance(r.id)
  await load()
}

async function load() {
  records.value = await api.getFinance() || []
  summary.value = await api.getFinanceSummary() || {}
}

onMounted(load)
</script>

<style scoped>
.finance-page { max-width: 800px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.add-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; }
.add-card h3 { font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 12px; }
.form-row { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; flex-wrap: wrap; }
.form-row input, .form-row select { padding: 9px 14px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 13px; background: #fafbfd; }
.btn-primary { padding: 10px 20px; background: #4f46e5; color: #fff; border: none; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; }
.type-toggle { display: flex; gap: 0; }
.type-toggle button { padding: 8px 16px; border: 1px solid #eef0f4; font-size: 13px; font-weight: 600; cursor: pointer; background: #fff; color: #6b7085; }
.type-toggle button:first-child { border-radius: 8px 0 0 8px; }
.type-toggle button:last-child { border-radius: 0 8px 8px 0; }
.type-toggle button.active { background: #4f46e5; color: #fff; border-color: #4f46e5; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px; text-align: center; }
.stat-value { font-size: 24px; font-weight: 800; }
.stat-income { color: #10b981; }
.stat-expense { color: #ef4444; }
.stat-label { font-size: 12px; color: #8b8fa8; margin-top: 4px; }
.chart-section { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; }
.section-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin-bottom: 14px; }
.cat-bars { }
.cat-bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.cat-bar-label { font-size: 12px; font-weight: 600; color: #6b7085; width: 60px; text-align: right; }
.cat-bar-track { flex: 1; height: 16px; background: #f0f1f5; border-radius: 8px; overflow: hidden; }
.cat-bar-fill { height: 100%; background: #ef4444; border-radius: 8px; transition: width 0.3s; }
.cat-bar-value { font-size: 12px; font-weight: 700; color: #1a1a2e; width: 80px; }
.record-item { display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid #f0f1f5; }
.record-date { font-size: 13px; font-weight: 600; color: #1a1a2e; min-width: 90px; }
.type-badge { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; }
.type-income { background: #ecfdf5; color: #10b981; }
.type-expense { background: #fef2f2; color: #ef4444; }
.amount { font-size: 14px; font-weight: 700; }
.amount-income { color: #10b981; }
.amount-expense { color: #ef4444; }
.cat-tag { padding: 2px 8px; border-radius: 100px; font-size: 11px; background: #f0f1f5; color: #6b7085; }
.record-note-inline { font-size: 12px; color: #8b8fa8; flex: 1; }
.btn-del { padding: 4px 12px; border: 1px solid #fecaca; border-radius: 6px; background: #fff; color: #ef4444; cursor: pointer; font-size: 11px; margin-left: auto; }
.empty { color: #b0b4c8; font-size: 13px; padding: 20px 0; text-align: center; }
</style>
