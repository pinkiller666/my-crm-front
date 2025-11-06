// FRONT — src/axios.js (script)
import axios from 'axios'
import { useAuthStore } from "@/stores/auth"

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api/'
const API_BASE_URL = rawBaseUrl.endsWith('/') ? rawBaseUrl : `${rawBaseUrl}/`

const api = axios.create({
  baseURL: API_BASE_URL,
})

const REFRESH_ENDPOINT = 'identity/token/refresh/'

let refreshPromise = null

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.access) {
    if (!config.headers) {
      config.headers = {}
    }
    config.headers.Authorization = `Bearer ${auth.access}`
  }
  return config
})

api.interceptors.response.use(
    (res) => res,
    async (err) => {
      // сетевые ошибки (нет response/нет config) — сразу наружу
      if (!err || !err.config) {
        return Promise.reject(err)
      }

      const auth = useAuthStore()
      const original = err.config

      const hasResponse = !!err.response
      const statusIs401 = hasResponse && err.response.status === 401
      const hasOriginal = !!original
      const alreadyRetried = hasOriginal && original._retry === true
      const requestUrl = hasOriginal && original.url ? original.url : ''

      if (statusIs401 && !alreadyRetried) {
        // не пытаемся рефрешить сам запрос рефреша
        if (requestUrl.indexOf(REFRESH_ENDPOINT) !== -1) {
          return Promise.reject(err)
        }

        // если нет рефреша — выходим из аккаунта
        if (!auth.refresh) {
          auth.logout()
          return Promise.reject(err)
        }

        // общий мьютекс на обновление токена (чтобы не плодить запросы)
        if (!refreshPromise) {
          refreshPromise = auth.refreshToken().finally(() => {
            refreshPromise = null
          })
        }

        const ok = await refreshPromise

        if (ok && auth.access) {
          original._retry = true
          if (!original.headers) {
            original.headers = {}
          }
          original.headers.Authorization = `Bearer ${auth.access}`
          return api(original)
        }
      }

      return Promise.reject(err)
    }
)

export { API_BASE_URL }
export default api
