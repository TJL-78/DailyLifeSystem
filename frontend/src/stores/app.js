import { defineStore } from 'pinia'
import api from '../api'

export const useAppStore = defineStore('app', {
  state: () => ({
    user: null,
    categories: [],
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
    }
  }
})
