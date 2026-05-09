import { createRouter, createWebHashHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Activities from '../views/Activities.vue'
import Calendar from '../views/Calendar.vue'
import Categories from '../views/Categories.vue'
import Habits from '../views/Habits.vue'
import Journal from '../views/Journal.vue'
import Statistics from '../views/Statistics.vue'
import Settings from '../views/Settings.vue'

const routes = [
  { path: '/', name: 'dashboard', component: Dashboard },
  { path: '/activities', name: 'activities', component: Activities },
  { path: '/calendar', name: 'calendar', component: Calendar },
  { path: '/categories', name: 'categories', component: Categories },
  { path: '/habits', name: 'habits', component: Habits },
  { path: '/journal', name: 'journal', component: Journal },
  { path: '/statistics', name: 'statistics', component: Statistics },
  { path: '/settings', name: 'settings', component: Settings },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
