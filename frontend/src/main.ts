import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'

import App from './App.vue'
import router from './router'
import zhTW from './locales/zh-TW'
import ja from './locales/ja'

import './assets/main.css'

// 版本兜底：避免旧 localStorage 值污染默认语言；v3 起默认日语
const LANG_VER = 'v3'
const _storedLang = localStorage.getItem('lang')
const _storedVer  = localStorage.getItem('lang_ver')
const savedLang = (_storedLang && _storedVer === LANG_VER) ? _storedLang : 'ja'
if (!_storedLang || _storedVer !== LANG_VER) {
  localStorage.setItem('lang', 'ja')
  localStorage.setItem('lang_ver', LANG_VER)
}

const i18n = createI18n({
  legacy: false,
  locale: savedLang,
  fallbackLocale: 'ja',
  messages: { 'zh-TW': zhTW, ja },
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)
app.mount('#app')
