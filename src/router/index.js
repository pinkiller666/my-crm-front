import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from "@/stores/auth"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/finance',
      name: 'finance-events',
      component: () => import('../views/FinanceEventsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/daily',
      name: 'daily-tasks',
      component: () => import('../views/DailyTasksView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: "login" })
  } else if ((to.name === 'login' || to.name === 'register') && auth.isAuthenticated) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
