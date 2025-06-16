import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import '@/assets/palette.css'

import App from './App.vue'
import router from './router'

// 🔹 Подключаем Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'



document.documentElement.setAttribute('data-theme', localStorage.getItem('theme') || 'classic')

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus) // 🔹 Используем Element Plus

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

app.mount('#app')
