import { defineStore } from "pinia"
import axios from "@/axios"

export const useAuthStore = defineStore("auth", {
  state: () => ({
    access: null,
    refresh: localStorage.getItem("refresh") || null,
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.access,
  },
  actions: {
    async login(username, password) {
      const res = await axios.post("/api/identity/token/", { username, password })
      this.access = res.data.access
      this.refresh = res.data.refresh
      localStorage.setItem("refresh", this.refresh)
      axios.defaults.headers.common["Authorization"] = `Bearer ${this.access}`

      // можно подтянуть профиль
      await this.fetchUser()
    },
    async fetchUser() {
      try {
        const res = await axios.get("/api/identity/profile/")
        this.user = res.data
      } catch (e) {
        this.user = null
      }
    },
    async refreshToken() {
      if (!this.refresh) return false
      try {
        const res = await axios.post("/api/identity/token/refresh/", {
          refresh: this.refresh,
        })
        this.access = res.data.access
        this.refresh = res.data.refresh
        localStorage.setItem("refresh", this.refresh)
        axios.defaults.headers.common["Authorization"] = `Bearer ${this.access}`
        return true
      } catch {
        this.logout()
        return false
      }
    },
    logout() {
      this.access = null
      this.refresh = null
      this.user = null
      localStorage.removeItem("refresh")
      delete axios.defaults.headers.common["Authorization"]
    },
    async init() {
      if (this.refresh && !this.access) {
        const ok = await this.refreshToken()
        if (ok) await this.fetchUser()
      }
    },
  },
})
