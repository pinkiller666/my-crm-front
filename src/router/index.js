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
      path: '/daily',
      name: 'daily-tasks',
      component: () => import('../views/DailyTasksView.vue'),
    meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  console.log(auth.isAuthenticated)

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: "login" })
  } else {
    next()
  }
})

export default router
