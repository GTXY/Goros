<template>
  <header class="sticky top-0 z-50 bg-dark/95 backdrop-blur border-b border-dark-border">
    <div class="max-w-screen-2xl mx-auto px-4 h-14 flex items-center gap-4">
      <!-- Logo -->
      <router-link to="/" class="flex items-center gap-1.5 shrink-0">
        <img src="/goros-feather.png" class="h-7 w-auto" alt="GOROS Logo" />
        <span class="text-gold font-bold text-xl tracking-widest font-mono">GOROS</span>
      </router-link>

      <!-- Stats -->
      <div class="hidden md:flex items-center gap-1 text-text-muted text-xs ml-2">
        <span>{{ t('header.sources', { n: stats?.sources?.length ?? 7 }) }}</span>
        <span class="mx-1 opacity-30">·</span>
        <span>{{ t('header.products', { n: (stats?.total_products ?? 0).toLocaleString() }) }}</span>
      </div>

      <div class="flex-1" />

      <!-- Last update -->
      <div class="hidden sm:block text-text-muted text-xs">
        {{ lastUpdateText }}
      </div>

      <!-- Sync button (hidden in production) -->
      <button
        v-if="allowManualSync"
        @click="handleSync"
        :disabled="syncing"
        class="flex items-center gap-1.5 border border-gold/50 text-gold text-xs px-3 py-1.5 rounded hover:bg-gold/10 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg
          class="w-3.5 h-3.5"
          :class="{ 'animate-spin': syncing }"
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
        {{ syncing ? t('header.syncing') : t('header.syncNow') }}
      </button>

      <!-- Language switch -->
      <div class="flex items-center text-xs gap-0">
        <button
          @click="setLang('ja')"
          :class="locale === 'ja' ? 'text-gold font-semibold' : 'text-text-muted hover:text-text-primary'"
          class="px-1.5 py-1 transition-colors"
        >{{ t('lang.ja') }}</button>
        <span class="text-dark-border">|</span>
        <button
          @click="setLang('zh-TW')"
          :class="locale === 'zh-TW' ? 'text-gold font-semibold' : 'text-text-muted hover:text-text-primary'"
          class="px-1.5 py-1 transition-colors"
        >{{ t('lang.zhTW') }}</button>
      </div>
    </div>

    <!-- Scrape panel -->
    <ScrapePanel v-if="showPanel" :status="scrapeStatus" @close="showPanel = false" />
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { scrapeApi } from '@/utils/api'
import { useProductStore } from '@/stores/productStore'
import type { ScrapeStatus } from '@/types'
import ScrapePanel from './ScrapePanel.vue'

const { t, locale } = useI18n()
const productStore = useProductStore()

const syncing = ref(false)
const showPanel = ref(false)
const scrapeStatus = ref<ScrapeStatus | null>(null)
let pollTimer: ReturnType<typeof setInterval> | null = null

const stats = computed(() => productStore.stats)

// Environment variables
const allowManualSync = __ALLOW_MANUAL_SYNC__

const lastUpdateText = computed(() => {
  const lastScrape = stats.value?.last_scrape
  if (!lastScrape) return t('header.never')
  const d = new Date(lastScrape)
  const now = new Date()
  const isToday = d.toDateString() === now.toDateString()
  const timeStr = d.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
  if (isToday) return t('header.lastUpdate', { time: t('header.today', { time: timeStr }) })
  return t('header.lastUpdate', { time: d.toLocaleDateString('zh-TW') })
})

function setLang(lang: string) {
  locale.value = lang
  localStorage.setItem('lang', lang)
}

async function handleSync() {
  if (syncing.value) return
  syncing.value = true
  showPanel.value = true
  try {
    await scrapeApi.trigger()
    startPolling()
  } catch {
    syncing.value = false
  }
}

function startPolling() {
  pollTimer = setInterval(async () => {
    try {
      const status = await scrapeApi.status()
      scrapeStatus.value = status
      if (!status.running) {
        syncing.value = false
        clearInterval(pollTimer!)
        pollTimer = null
        // 刷新数据
        await productStore.fetchStats()
        await productStore.fetchProducts()
      }
    } catch {
      syncing.value = false
      clearInterval(pollTimer!)
    }
  }, 2000)
}

onMounted(() => {
  productStore.fetchStats()
})
</script>
