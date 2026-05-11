<template>
  <div class="settings-page">
    <h1 class="page-title">{{ t('settings') }}</h1>

    <div class="settings-card">
      <h2 class="section-title">{{ t('darkMode') }}</h2>
      <div class="toggle-row">
        <span>{{ t('darkMode') }}</span>
        <button :class="{ active: store.darkMode }" class="toggle-btn" @click="store.toggleDarkMode()">
          {{ store.darkMode ? 'ON' : 'OFF' }}
        </button>
      </div>
    </div>

    <div class="settings-card">
      <h2 class="section-title">{{ t('enableNotifications') }}</h2>
      <div class="toggle-row">
        <span>{{ t('enableNotifications') }}</span>
        <button :class="{ active: store.notificationsEnabled }" class="toggle-btn" @click="toggleNotifications">
          {{ store.notificationsEnabled ? 'ON' : 'OFF' }}
        </button>
      </div>
      <div v-if="notifMsg" class="msg">{{ notifMsg }}</div>
    </div>

    <div class="settings-card">
      <h2 class="section-title">{{ t('langSwitch') }}</h2>
      <div class="lang-row">
        <button :class="{ active: currentLang === 'zh' }" @click="switchLang('zh')">中文</button>
        <button :class="{ active: currentLang === 'en' }" @click="switchLang('en')">English</button>
      </div>
    </div>

    <div class="settings-card">
      <h2 class="section-title">{{ t('avatar') }}</h2>
      <div class="avatar-section">
        <div class="avatar-preview">
          <img v-if="store.user?.avatar_url" :src="store.user.avatar_url" />
          <svg v-else width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#b0b4c8" stroke-width="1.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </div>
        <div>
          <label class="btn-upload">
            {{ t('chooseAvatar') }}
            <input type="file" accept="image/*" @change="uploadAvatar" hidden />
          </label>
          <p class="hint">{{ t('avatarHint') }}</p>
        </div>
      </div>
    </div>

    <div class="settings-card">
      <h2 class="section-title">{{ t('profile') }}</h2>
      <div class="form-group">
        <label>{{ t('displayName') }}</label>
        <input v-model="profile.display_name" />
      </div>
      <div class="form-group">
        <label>{{ t('emailPlaceholder') }}</label>
        <input v-model="profile.email" type="email" />
      </div>
      <div class="form-group">
        <label>{{ t('phonePlaceholder') }}</label>
        <input v-model="profile.phone" />
      </div>
      <button class="btn-primary" @click="saveProfile">{{ t('save') }}</button>
      <div v-if="profileMsg" class="msg">{{ profileMsg }}</div>
    </div>

    <div class="settings-card">
      <h2 class="section-title">{{ t('changePassword') }}</h2>
      <div class="form-group">
        <label>{{ t('oldPw') }}</label>
        <input v-model="pw.old_password" type="password" />
      </div>
      <div class="form-group">
        <label>{{ t('newPw') }}</label>
        <input v-model="pw.new_password" type="password" />
      </div>
      <button class="btn-primary" @click="changePw">{{ t('changePwBtn') }}</button>
      <div v-if="pwMsg" class="msg">{{ pwMsg }}</div>
    </div>

    <div class="settings-card">
      <h2 class="section-title">{{ t('exportData') }}</h2>
      <div class="backup-row">
        <button class="btn-primary" @click="exportData">{{ t('exportData') }}</button>
        <label class="btn-upload">
          {{ t('importData') }}
          <input type="file" accept=".json" @change="importData" hidden />
        </label>
      </div>
      <div v-if="backupMsg" class="msg">{{ backupMsg }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from '../i18n'
import { useAppStore } from '../stores/app'
import api from '../api'

const { t, currentLang, switchLang } = useI18n()
const store = useAppStore()
const profile = ref({ display_name: '', email: '', phone: '' })
const pw = ref({ old_password: '', new_password: '' })
const profileMsg = ref('')
const pwMsg = ref('')
const notifMsg = ref('')
const backupMsg = ref('')

onMounted(() => {
  if (store.user) {
    profile.value.display_name = store.user.display_name || ''
    profile.value.email = store.user.email || ''
    profile.value.phone = store.user.phone || ''
  }
})

async function saveProfile() {
  if (profile.value.phone && !/^1\d{10}$/.test(profile.value.phone)) {
    profileMsg.value = t('phoneInvalid')
    return
  }
  await api.updateProfile(profile.value)
  profileMsg.value = t('profileUpdated')
  await store.loadUser()
  setTimeout(() => profileMsg.value = '', 2000)
}

async function changePw() {
  if (!pw.value.old_password || !pw.value.new_password) return
  await api.changePassword(pw.value)
  pwMsg.value = t('pwChanged')
  pw.value = { old_password: '', new_password: '' }
  setTimeout(() => pwMsg.value = '', 2000)
}

async function uploadAvatar(e) {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('avatar', file)
  await api.uploadAvatar(fd)
  await store.loadUser()
  e.target.value = ''
}

async function toggleNotifications() {
  const ok = await store.requestNotificationPermission()
  notifMsg.value = ok ? t('notificationsEnabled') : t('notificationsDenied')
  setTimeout(() => notifMsg.value = '', 2000)
}

async function exportData() {
  const data = await api.exportAllData()
  if (!data) return
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'daily-life-backup.json'
  a.click()
  backupMsg.value = t('dataExported')
  setTimeout(() => backupMsg.value = '', 2000)
}

async function importData(e) {
  const file = e.target.files[0]
  if (!file) return
  const text = await file.text()
  try {
    const data = JSON.parse(text)
    await api.importData(data)
    backupMsg.value = t('dataImported')
    setTimeout(() => backupMsg.value = '', 2000)
  } catch (err) {
    backupMsg.value = 'Invalid JSON file'
  }
  e.target.value = ''
}
</script>

<style scoped>
.settings-page { max-width: 640px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 24px; }
.section-title { font-size: 15px; font-weight: 700; color: #1a1a2e; margin-bottom: 14px; }
.settings-card { background: #fff; border: 1px solid #eef0f4; border-radius: 16px; padding: 24px 28px; margin-bottom: 16px; }
.lang-row { display: flex; gap: 8px; }
.lang-row button { padding: 8px 20px; border: 1px solid #eef0f4; border-radius: 8px; background: #fff; cursor: pointer; font-size: 13px; font-weight: 500; color: #6b7085; }
.lang-row button.active { background: #4f46e5; color: #fff; border-color: #4f46e5; }
.avatar-section { display: flex; gap: 20px; align-items: center; }
.avatar-preview { width: 72px; height: 72px; border-radius: 50%; background: #f0f1f5; overflow: hidden; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.avatar-preview img { width: 100%; height: 100%; object-fit: cover; }
.btn-upload { padding: 8px 18px; background: #4f46e5; color: #fff; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; display: inline-block; }
.hint { font-size: 11px; color: #b0b4c8; margin-top: 6px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 12px; font-weight: 600; color: #6b7085; margin-bottom: 6px; }
.form-group input { width: 100%; padding: 10px 14px; border: 1px solid #eef0f4; border-radius: 10px; font-size: 13px; background: #fafbfd; }
.form-group input:focus { outline: none; border-color: #4f46e5; background: #fff; }
.btn-primary { padding: 10px 24px; background: #4f46e5; color: #fff; border: none; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; }
.msg { margin-top: 10px; color: #10b981; font-size: 13px; font-weight: 600; }
.toggle-row { display: flex; align-items: center; justify-content: space-between; }
.toggle-btn { padding: 8px 20px; border: 1px solid #eef0f4; border-radius: 8px; background: #fff; cursor: pointer; font-size: 13px; font-weight: 600; color: #6b7085; }
.toggle-btn.active { background: #4f46e5; color: #fff; border-color: #4f46e5; }
.backup-row { display: flex; gap: 12px; }
</style>
