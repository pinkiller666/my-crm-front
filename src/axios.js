import axios from 'axios'
import { useAuthStore } from "@/stores/auth"

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1/'
const API_BASE_URL = rawBaseUrl.endsWith('/') ? rawBaseUrl : `${rawBaseUrl}/`

const api = axios.create({
  baseURL: API_BASE_URL,
})

const REFRESH_ENDPOINT = 'identity/token/refresh/'

let refreshPromise = null

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.access) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${auth.access}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const auth = useAuthStore()
    const original = err.config

    if (err.response?.status === 401 && !original?._retry) {
      const requestUrl = original?.url || ''

      if (requestUrl.includes(REFRESH_ENDPOINT)) {
        return Promise.reject(err)
      }

      if (!auth.refresh) {
        auth.logout()
        return Promise.reject(err)
      }

      if (!refreshPromise) {
        refreshPromise = auth
          .refreshToken()
          .finally(() => {
            refreshPromise = null
          })
      }

      const ok = await refreshPromise

      if (ok && auth.access) {
        original._retry = true
        original.headers = {
          ...(original.headers ?? {}),
          Authorization: `Bearer ${auth.access}`,
        }
        return api(original)
      }
    }
    return Promise.reject(err)
  }
)

export { API_BASE_URL }
export default api
