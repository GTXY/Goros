<template>
  <div class="min-h-screen pb-20">
    <!-- Mobile Header -->
    <header class="sticky top-0 z-50 bg-dark/95 backdrop-blur border-b border-dark-border px-4 h-12 flex items-center justify-between">
      <span class="text-gold font-bold font-mono tracking-widest">GOROS</span>
      <div class="flex items-center gap-2">
        <span class="text-text-muted text-xs">{{ productStore.total.toLocaleString() }}</span>
        <button @click="handleSync" :disabled="syncing"
          class="border border-gold/50 text-gold text-xs px-2.5 py-1 rounded"
        >
          <svg class="w-3 h-3 inline mr-1" :class="{ 'animate-spin': syncing }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          {{ syncing ? '同步中' : '同步' }}
        </button>
        <button @click="filterOpen = !filterOpen" class="border border-dark-border text-text-secondary text-xs px-2.5 py-1 rounded">
          <svg class="w-3.5 h-3.5 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h18M6 8h12M10 12h4"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- Mobile filter drawer -->
    <div v-if="filterOpen" class="fixed inset-0 z-50 bg-dark/95 overflow-y-auto p-4">
      <div class="flex items-center justify-between mb-4">
        <span class="text-text-primary font-semibold">篩選</span>
        <button @click="filterOpen = false" class="text-text-muted">✕</button>
      </div>

      <!-- Sort -->
      <div class="mb-4">
        <p class="text-xs text-text-muted mb-2">排序</p>
        <select v-model="filterStore.sort" @change="applyFilter" class="input-dark w-full text-sm">
          <option value="scraped_at_desc">最新更新</option>
          <option value="price_asc">價格從低到高</option>
          <option value="price_desc">價格從高到低</option>
        </select>
      </div>

      <!-- In stock toggle -->
      <label class="flex items-center gap-2 mb-4">
        <input type="checkbox" v-model="localInStock" class="accent-gold" />
        <span class="text-sm text-text-secondary">僅顯示有貨</span>
      </label>

      <!-- Sources -->
      <div class="mb-4">
        <p class="text-xs text-text-muted mb-2">來源平台</p>
        <div class="grid grid-cols-2 gap-2">
          <label v-for="s in allSources" :key="s.key" class="flex items-center gap-2">
            <input type="checkbox" :value="s.key" v-model="localSources" class="accent-gold" />
            <span class="text-xs text-text-secondary">{{ s.name }}</span>
          </label>
        </div>
      </div>

      <button @click="applyFilter" class="btn-gold w-full py-3 text-sm">套用</button>
    </div>

    <!-- Product list (single column on mobile) -->
    <div class="px-3 py-3 space-y-2">
      <LoadingSpinner v-if="loading" />

      <div
        v-else-if="!loading && products.length === 0"
        class="text-center py-20"
      >
        <p class="text-text-muted text-sm">{{ total === 0 ? '請點擊同步按鈕獲取資料' : '無符合條件的商品' }}</p>
      </div>

      <!-- List-style cards (horizontal) -->
      <router-link
        v-for="p in products"
        :key="p.id"
        :to="`/m/product/${p.id}`"
        class="flex gap-3 bg-dark-card border border-dark-border rounded-lg p-2.5 hover:border-gold/40 transition-all"
      >
        <div class="w-16 h-16 flex-shrink-0 bg-dark rounded overflow-hidden">
          <img
            v-if="p.images?.[0]"
            :src="p.images[0]"
            :alt="p.title"
            loading="lazy"
            class="w-full h-full object-contain"
          />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-text-primary text-xs leading-snug line-clamp-2 font-jp mb-1">{{ p.title }}</p>
          <div class="flex items-center gap-1.5">
            <span class="badge-gold text-[10px]">{{ p.source_name }}</span>
            <span v-if="!p.available" class="text-text-muted text-[10px]">售出</span>
          </div>
          <p class="text-gold font-mono font-medium text-sm mt-1">
            {{ formatPrice(p.price_raw, p.price_jpy) }}
          </p>
        </div>
      </router-link>
    </div>

    <!-- Pagination -->
    <div v-if="pages > 1" class="flex justify-center gap-2 py-4">
      <button @click="onPage(filterStore.page - 1)" :disabled="filterStore.page <= 1"
        class="btn-outline text-xs px-3 py-1.5 disabled:opacity-30">‹</button>
      <span class="text-text-muted text-xs self-center">{{ filterStore.page }} / {{ pages }}</span>
      <button @click="onPage(filterStore.page + 1)" :disabled="filterStore.page >= pages"
        class="btn-outline text-xs px-3 py-1.5 disabled:opacity-30">›</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useProductStore } from '@/stores/productStore'
import { useFilterStore } from '@/stores/filterStore'
import { scrapeApi } from '@/utils/api'
import { formatPrice } from '@/utils/currency'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const productStore = useProductStore()
const filterStore = useFilterStore()

const products = computed(() => productStore.products)
const total = computed(() => productStore.total)
const pages = computed(() => productStore.pages)
const loading = computed(() => productStore.loading)

const filterOpen = ref(false)
const syncing = ref(false)

const allSources = [
  { key: 'deltaone_jp', name: 'DeltaOne JP' },
  { key: 'deltaone_hk', name: 'DeltaOne HK' },
  { key: 'corner', name: 'Corner' },
  { key: 'nativefeather', name: 'Native Feather' },
  { key: 'truemark', name: 'TrueMark' },
  { key: 'fivesix', name: 'FiveSix' },
  { key: 'rinkan', name: 'RINKAN' },
]

const localSources = ref([...filterStore.sources])
const localInStock = ref(filterStore.inStock !== false)

async function handleSync() {
  syncing.value = true
  try {
    await scrapeApi.trigger()
    const poll = setInterval(async () => {
      const s = await scrapeApi.status()
      if (!s.running) {
        clearInterval(poll)
        syncing.value = false
        await productStore.fetchProducts()
      }
    }, 2000)
  } catch {
    syncing.value = false
  }
}

function applyFilter() {
  filterStore.sources = localSources.value
  filterStore.inStock = localInStock.value ? true : null
  filterStore.setPage(1)
  productStore.fetchProducts()
  filterOpen.value = false
}

function onPage(p: number) {
  filterStore.setPage(p)
  productStore.fetchProducts()
  window.scrollTo({ top: 0 })
}

onMounted(() => {
  productStore.fetchProducts()
})
</script>
