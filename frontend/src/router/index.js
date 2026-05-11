import { createRouter, createWebHashHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Activities from '../views/Activities.vue'
import Calendar from '../views/Calendar.vue'
import Categories from '../views/Categories.vue'
import Habits from '../views/Habits.vue'
import Journal from '../views/Journal.vue'
import Statistics from '../views/Statistics.vue'
import Settings from '../views/Settings.vue'
import Pomodoro from '../views/Pomodoro.vue'
import Goals from '../views/Goals.vue'
import Heatmap from '../views/Heatmap.vue'
import Templates from '../views/Templates.vue'
import Tags from '../views/Tags.vue'
import Kanban from '../views/Kanban.vue'

const routes = [
  { path: '/', name: 'dashboard', component: Dashboard },
  { path: '/activities', name: 'activities', component: Activities },
  { path: '/calendar', name: 'calendar', component: Calendar },
  { path: '/categories', name: 'categories', component: Categories },
  { path: '/habits', name: 'habits', component: Habits },
  { path: '/journal', name: 'journal', component: Journal },
  { path: '/statistics', name: 'statistics', component: Statistics },
  { path: '/settings', name: 'settings', component: Settings },
  { path: '/pomodoro', name: 'pomodoro', component: Pomodoro },
  { path: '/goals', name: 'goals', component: Goals },
  { path: '/heatmap', name: 'heatmap', component: Heatmap },
  { path: '/templates', name: 'templates', component: Templates },
  { path: '/tags', name: 'tags', component: Tags },
  { path: '/kanban', name: 'kanban', component: Kanban },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
