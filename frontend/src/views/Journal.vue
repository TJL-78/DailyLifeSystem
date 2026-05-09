<template>
  <div class="journal-page">
    <h1 class="page-title">{{ t('journalTitle') }}</h1>

    <div class="write-card">
      <h2 class="section-title">{{ t('writeJournal') }}</h2>
      <div class="form-row">
        <label>{{ t('journalDate') }}</label>
        <input v-model="form.date" type="date" />
      </div>
      <div class="form-row">
        <label>{{ t('weather') }}</label>
        <select v-model="form.weather">
          <option value="">--</option>
          <option value="sunny">{{ t('weatherSunny') }}</option>
          <option value="cloudy">{{ t('weatherCloudy') }}</option>
          <option value="overcast">{{ t('weatherOvercast') }}</option>
          <option value="rainy">{{ t('weatherRainy') }}</option>
          <option value="snowy">{{ t('weatherSnowy') }}</option>
          <option value="windy">{{ t('weatherWindy') }}</option>
        </select>
      </div>
      <div class="form-row">
        <label>{{ t('mood') }}</label>
        <select v-model="form.mood">
          <option value="">--</option>
          <option value="happy">{{ t('moodHappy') }}</option>
          <option value="calm">{{ t('moodCalm') }}</option>
          <option value="sad">{{ t('moodSad') }}</option>
          <option value="angry">{{ t('moodAngry') }}</option>
          <option value="tired">{{ t('moodTired') }}</option>
          <option value="excited">{{ t('moodExcited') }}</option>
        </select>
      </div>
      <div class="form-row">
        <label>{{ t('journalContent') }}</label>
        <textarea v-model="form.content" :placeholder="t('contentPlaceholder')" rows="6"></textarea>
      </div>
      <div class="form-row">
        <label>{{ t('clickUploadImages') }}</label>
        <div class="image-upload">
          <div v-for="(img, i) in form.images" :key="i" class="img-preview">
            <img :src="img" />
            <button class="img-del" @click="form.images.splice(i, 1)">✕</button>
          </div>
          <label v-if="form.images.length < 9" class="img-add">
            <input type="file" accept="image/*" @change="uploadImage" hidden />
            <span>+</span>
          </label>
        </div>
      </div>
      <div class="form-actions">
        <button class="btn-primary" @click="saveJournal">{{ t('saveJournal') }}</button>
        <button class="btn-secondary" @click="clearForm">{{ t('clearJournal') }}</button>
      </div>
      <div v-if="saveMsg" class="save-msg">{{ saveMsg }}</div>
    </div>

    <div class="history-section">
      <h2 class="section-title">{{ t('journalHistory') }}</h2>
      <div v-if="!journals.length" class="empty">{{ t('noJournals') }}</div>
      <div v-for="j in journals" :key="j.id" class="journal-card">
        <div class="journal-header" @click="j._expanded = !j._expanded">
          <div class="journal-date">{{ j.date }}</div>
          <div class="journal-tags">
            <span v-if="j.weather" class="jtag">{{ weatherLabel(j.weather) }}</span>
            <span v-if="j.mood" class="jtag">{{ moodLabel(j.mood) }}</span>
          </div>
          <button class="btn-del" @click.stop="deleteJournal(j)">{{ t('delete') }}</button>
        </div>
        <div v-if="j._expanded" class="journal-body">
          <p class="journal-text">{{ j.content }}</p>
          <div v-if="j.images && j.images.length" class="journal-images">
            <img v-for="(img, i) in j.images" :key="i" :src="img" />
          </div>
          <div class="comment-section">
            <div v-for="c in (j._comments || [])" :key="c.id" class="comment-item">
              <span class="comment-text">{{ c.content }}</span>
              <button class="comment-del" @click="deleteComment(j, c)">✕</button>
            </div>
            <div class="comment-input">
              <input v-model="j._newComment" :placeholder="t('commentPlaceholder')" @keypress.enter="addComment(j)" />
              <button @click="addComment(j)">{{ t('sendComment') }}</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useI18n } from '../i18n'
import api from '../api'

const { t } = useI18n()
const today = new Date().toISOString().slice(0, 10)
const form = ref({ date: today, weather: '', mood: '', content: '', images: [] })
const journals = ref([])
const saveMsg = ref('')

const weatherMap = { sunny: 'weatherSunny', cloudy: 'weatherCloudy', overcast: 'weatherOvercast', rainy: 'weatherRainy', snowy: 'weatherSnowy', windy: 'weatherWindy' }
const moodMap = { happy: 'moodHappy', calm: 'moodCalm', sad: 'moodSad', angry: 'moodAngry', tired: 'moodTired', excited: 'moodExcited' }
function weatherLabel(w) { return t(weatherMap[w] || w) }
function moodLabel(m) { return t(moodMap[m] || m) }

async function loadJournals() {
  const res = await api.getJournals() || []
  journals.value = (Array.isArray(res) ? res : []).map(j => ({ ...j, _expanded: false, _newComment: '', _comments: [] }))
}

async function loadExistingJournal() {
  const existing = await api.getJournalByDate(form.value.date)
  if (existing) {
    form.value.weather = existing.weather || ''
    form.value.mood = existing.mood || ''
    form.value.content = existing.content || ''
    form.value.images = existing.images || []
  }
}

watch(() => form.value.date, loadExistingJournal)

async function saveJournal() {
  if (!form.value.content.trim()) return
  await api.saveJournal(form.value)
  saveMsg.value = t('journalSaved')
  setTimeout(() => saveMsg.value = '', 2000)
  await loadJournals()
}

function clearForm() {
  if (!confirm(t('confirmClearJournal'))) return
  form.value = { date: today, weather: '', mood: '', content: '', images: [] }
}

async function uploadImage(e) {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('image', file)
  const res = await api.uploadJournalImage(fd)
  if (res && res.url) form.value.images.push(res.url)
  e.target.value = ''
}

async function deleteJournal(j) {
  if (!confirm(t('confirmDeleteJournal'))) return
  await api.deleteJournal(j.id)
  await loadJournals()
}

async function addComment(j) {
  if (!j._newComment?.trim()) return
  await api.addJournalComment(j.id, j._newComment)
  j._newComment = ''
  j._comments = await api.getJournalComments(j.id) || []
}

async function deleteComment(j, c) {
  await api.deleteJournalComment(c.id)
  j._comments = await api.getJournalComments(j.id) || []
}

onMounted(async () => { await loadJournals(); await loadExistingJournal() })
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.section-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin-bottom: 16px; }
.write-card { background: #fff; border: 1px solid #eef0f4; border-radius: 16px; padding: 24px 28px; margin-bottom: 32px; }
.form-row { margin-bottom: 14px; }
.form-row label { display: block; font-size: 12px; font-weight: 600; color: #6b7085; margin-bottom: 6px; }
.form-row input, .form-row select, .form-row textarea { width: 100%; padding: 10px 14px; border: 1px solid #eef0f4; border-radius: 10px; font-size: 13px; background: #fafbfd; font-family: inherit; }
.form-row input:focus, .form-row select:focus, .form-row textarea:focus { outline: none; border-color: #4f46e5; background: #fff; }
.form-row textarea { resize: vertical; }
.image-upload { display: flex; gap: 8px; flex-wrap: wrap; }
.img-preview { width: 80px; height: 80px; border-radius: 8px; overflow: hidden; position: relative; border: 1px solid #eef0f4; }
.img-preview img { width: 100%; height: 100%; object-fit: cover; }
.img-del { position: absolute; top: 2px; right: 2px; background: rgba(0,0,0,0.5); color: #fff; border: none; border-radius: 50%; width: 18px; height: 18px; cursor: pointer; font-size: 10px; }
.img-add { width: 80px; height: 80px; border: 2px dashed #d1d5e0; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 24px; color: #b0b4c8; }
.img-add:hover { border-color: #4f46e5; color: #4f46e5; }
.form-actions { display: flex; gap: 8px; }
.btn-primary { padding: 10px 24px; background: #4f46e5; color: #fff; border: none; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; }
.btn-secondary { padding: 10px 24px; background: #fff; color: #6b7085; border: 1px solid #eef0f4; border-radius: 10px; font-size: 13px; cursor: pointer; }
.save-msg { margin-top: 10px; color: #10b981; font-size: 13px; font-weight: 600; }
.journal-card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; margin-bottom: 10px; overflow: hidden; }
.journal-header { display: flex; align-items: center; gap: 12px; padding: 14px 20px; cursor: pointer; }
.journal-header:hover { background: #fafbfd; }
.journal-date { font-size: 14px; font-weight: 700; color: #1a1a2e; }
.journal-tags { display: flex; gap: 6px; flex: 1; }
.jtag { font-size: 12px; padding: 2px 10px; border-radius: 100px; background: #f0f1f5; color: #6b7085; }
.btn-del { padding: 5px 12px; border: 1px solid #fecaca; border-radius: 8px; background: #fff; color: #ef4444; cursor: pointer; font-size: 11px; }
.journal-body { padding: 0 20px 20px; }
.journal-text { font-size: 14px; line-height: 1.7; color: #3a3a4e; white-space: pre-wrap; }
.journal-images { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.journal-images img { width: 100px; height: 100px; object-fit: cover; border-radius: 8px; border: 1px solid #eef0f4; }
.comment-section { margin-top: 16px; border-top: 1px solid #eef0f4; padding-top: 12px; }
.comment-item { display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 13px; }
.comment-text { flex: 1; color: #3a3a4e; }
.comment-del { border: none; background: none; color: #ef4444; cursor: pointer; font-size: 11px; }
.comment-input { display: flex; gap: 6px; margin-top: 8px; }
.comment-input input { flex: 1; padding: 8px 12px; border: 1px solid #eef0f4; border-radius: 8px; font-size: 12px; }
.comment-input button { padding: 8px 16px; background: #4f46e5; color: #fff; border: none; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; }
.empty { color: #b0b4c8; font-size: 13px; padding: 40px 0; text-align: center; }
</style>
