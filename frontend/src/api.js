const API = '/api'

async function request(url, options = {}) {
  const res = await fetch(url, options)
  if (res.status === 401) {
    window.location.href = '/login'
    return null
  }
  return res
}

async function json(url, options = {}) {
  const res = await request(url, options)
  if (!res) return null
  const data = await res.json()
  if (!res.ok) {
    const err = new Error(data?.error || data?.detail || 'Request failed')
    err.status = res.status
    throw err
  }
  return data
}

function post(url, body) {
  return json(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
}

function put(url, body) {
  return json(url, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
}

function del(url) {
  return request(url, { method: 'DELETE' })
}

export default {
  getMe: () => json(`${API}/auth/me`),
  logout: () => request(`${API}/auth/logout`, { method: 'POST' }),
  updateProfile: (data) => put(`${API}/auth/profile`, data),
  changePassword: (data) => put(`${API}/auth/password`, data),
  uploadAvatar: (formData) => request(`${API}/auth/avatar`, { method: 'POST', body: formData }).then(r => r?.json()),
  getLockout: () => json(`${API}/auth/lockout`),

  getCategories: () => json(`${API}/categories`),
  createCategory: (data) => post(`${API}/categories`, data),
  deleteCategory: (id) => del(`${API}/categories/${id}`),

  getActivities: (params = {}) => {
    const q = new URLSearchParams(params).toString()
    return json(`${API}/activities?${q}`)
  },
  createActivity: (data) => post(`${API}/activities`, data),
  completeActivity: (id) => request(`${API}/activities/${id}/complete`, { method: 'POST' }),
  startActivity: (id) => request(`${API}/activities/${id}/start`, { method: 'POST' }),
  cancelActivity: (id) => request(`${API}/activities/${id}/cancel`, { method: 'POST' }),
  deleteActivity: (id) => del(`${API}/activities/${id}`),
  searchActivities: (q) => json(`${API}/activities/search?q=${encodeURIComponent(q)}`),
  getSubtasks: (id) => json(`${API}/activities/${id}/subtasks`),
  createSubtask: (id, data) => post(`${API}/activities/${id}/subtasks`, data),
  getCalendarEvents: (start, end) => json(`${API}/activities/calendar?start=${start}&end=${end}`),

  getStats: () => json(`${API}/stats`),
  getDetailedStats: () => json(`${API}/stats/detailed`),

  getHabits: () => json(`${API}/habits`),
  createHabit: (data) => post(`${API}/habits`, data),
  deleteHabit: (id) => del(`${API}/habits/${id}`),
  checkinHabit: (id, date) => post(`${API}/habits/${id}/checkin`, { date }),
  uncheckinHabit: (id, date) => post(`${API}/habits/${id}/uncheckin`, { date }),
  getHabitRecords: (id, start, end) => json(`${API}/habits/${id}/records?start=${start}&end=${end}`),

  getJournals: () => json(`${API}/journals`),
  getJournalByDate: async (date) => {
    const res = await request(`${API}/journals/date/${date}`)
    if (res && res.ok) return res.json()
    return null
  },
  saveJournal: (data) => post(`${API}/journals`, data),
  deleteJournal: (id) => del(`${API}/journals/${id}`),
  uploadJournalImage: (formData) => request(`${API}/journals/upload-image`, { method: 'POST', body: formData }).then(r => r?.json()),
  getJournalComments: (id) => json(`${API}/journals/${id}/comments`),
  addJournalComment: (id, content) => post(`${API}/journals/${id}/comments`, { content }),
  deleteJournalComment: (id) => del(`${API}/journals/comments/${id}`),

  // Pomodoro
  getPomodoroSessions: (params = {}) => { const q = new URLSearchParams(params).toString(); return json(`${API}/pomodoro/sessions?${q}`) },
  createPomodoroSession: (data) => post(`${API}/pomodoro/sessions`, data),
  getPomodoroStats: (date) => json(`${API}/pomodoro/stats?date=${date}`),

  // Goals
  getGoals: () => json(`${API}/goals`),
  createGoal: (data) => post(`${API}/goals`, data),
  deleteGoal: (id) => del(`${API}/goals/${id}`),
  getGoalProgress: (id) => json(`${API}/goals/${id}/progress`),
  addGoalProgress: (id, data) => post(`${API}/goals/${id}/progress`, data),

  // Heatmap
  getHeatmapData: (year) => json(`${API}/stats/heatmap?year=${year}`),
  getMonthlyReport: (year, month) => json(`${API}/stats/monthly-report?year=${year}&month=${month}`),

  // Templates
  getTemplates: () => json(`${API}/templates`),
  createTemplate: (data) => post(`${API}/templates`, data),
  deleteTemplate: (id) => del(`${API}/templates/${id}`),
  useTemplate: (id) => post(`${API}/templates/${id}/use`, {}),

  // Tags
  getTags: () => json(`${API}/tags`),
  updateTag: (id, data) => put(`${API}/tags/${id}`, data),
  deleteTag: (id) => del(`${API}/tags/${id}`),

  // Sharing
  shareActivity: (id, data) => post(`${API}/activities/${id}/share`, data),
  getActivityShares: (id) => json(`${API}/activities/${id}/shares`),

  // Backup
  exportAllData: () => json(`${API}/backup/export`),
  importData: (data) => post(`${API}/backup/import`, data),

  // Dashboard
  getDashboard: () => json(`${API}/dashboard`),

  // Recurring
  generateRecurring: () => post(`${API}/activities/generate-recurring`, {}),
}
