import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AddEventPage from '@/views/AddEventPage.vue'
import MonthProgressView from '@/views/MonthProgressView.vue'  // ✅ правильный импорт

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'), // Ленивая загрузка
    },
    {
      path: '/add-event',
      name: 'add-event',
      component: AddEventPage,
    },
    {
      path: '/progress',
      name: 'progress',
      component: MonthProgressView,
    },
  ],
})

export default router
