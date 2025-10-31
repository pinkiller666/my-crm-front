import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import '@/assets/palette.css'

import App from './App.vue'
import router from './router'
import { useAuthStore } from "@/stores/auth"

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import VueDragScroller from  "vue-drag-scroller"

document.documentElement.setAttribute('data-theme', localStorage.getItem('theme') || 'classic')

const app = createApp(App)

app.use(createPinia())

const auth = useAuthStore()
await auth.init()

app.use(router)
app.use(VueDragScroller)
app.use(ElementPlus)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}



app.mount('#app')
