import axios from 'axios'
import { useAuthStore } from "@/stores/auth"

const api = axios.create({
  baseURL: '/',
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.access) {
    config.headers.Authorization = `Bearer ${auth.access}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const auth = useAuthStore()
    const original = err.config

    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      await auth.refreshToken()
      if (auth.access) {
        original.headers.Authorization = `Bearer ${auth.access}`
        return api(original)
      }
    }
    return Promise.reject(err)
  }
)

export default api
