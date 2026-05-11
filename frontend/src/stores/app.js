import { defineStore } from 'pinia'
import api from '../api'

export const useAppStore = defineStore('app', {
  state: () => ({
    user: null,
    categories: [],
    darkMode: localStorage.getItem('darkMode') === 'true',
    notificationsEnabled: Notification?.permission === 'granted',
  }),
  actions: {
    async loadUser() {
      const data = await api.getMe()
      if (data) this.user = data.user
    },
    async loadCategories() {
      this.categories = await api.getCategories() || []
    },
    async logout() {
      await api.logout()
      window.location.href = '/login'
    },
    toggleDarkMode() {
      this.darkMode = !this.darkMode
      localStorage.setItem('darkMode', this.darkMode)
      document.documentElement.setAttribute('data-theme', this.darkMode ? 'dark' : 'light')
    },
    initTheme() {
      document.documentElement.setAttribute('data-theme', this.darkMode ? 'dark' : 'light')
    },
    async requestNotificationPermission() {
      if (!('Notification' in window)) return false
      const perm = await Notification.requestPermission()
      this.notificationsEnabled = perm === 'granted'
      return this.notificationsEnabled
    },
    scheduleNotification(title, body, delayMs) {
      if (!this.notificationsEnabled) return
      setTimeout(() => {
        new Notification(title, { body })
      }, delayMs)
    }
  }
})
