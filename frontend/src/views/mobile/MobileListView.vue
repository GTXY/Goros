<template>
  <div class="min-h-screen pb-20">
    <!-- Mobile Header -->
    <header class="sticky top-0 z-50 bg-dark/95 backdrop-blur border-b border-dark-border px-4 h-12 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-1 shrink-0">
          <img src="/goros-feather.png" class="h-6 w-auto" alt="GOROS Logo" />
          <span class="text-gold font-bold text-lg tracking-widest font-mono">GOROS</span>
        </router-link>
        <span class="text-text-muted text-xs">• {{ productStore.total.toLocaleString() }}件</span>
      </div>
      <div class="flex items-center gap-2">
        <button v-if="allowManualSync" @click="handleSync" :disabled="syncing"
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

      <!-- Categories -->
      <div class="mb-4">
        <p class="text-xs text-text-muted mb-2">商品分類</p>
        <div class="grid grid-cols-2 gap-2">
          <label v-for="cat in allCategories" :key="cat" class="flex items-center gap-2">
            <input type="checkbox" :value="cat" v-model="localCategories" class="accent-gold" />
            <span class="text-xs text-text-secondary">{{ cat }}</span>
          </label>
        </div>
      </div>

      <button @click="applyFilter" class="btn-gold w-full py-3 text-sm">套用</button>
    </div>

    <!-- Product list (two-column grid on mobile) -->
    <div class="px-3 py-3">
      <LoadingSpinner v-if="loading" />

      <div
        v-else-if="!loading && products.length === 0"
        class="text-center py-20"
      >
        <p class="text-text-muted text-sm">{{ total === 0 ? '請點擊同步按鈕獲取資料' : '無符合條件的商品' }}</p>
      </div>

      <!-- Two-column grid with big images -->
      <div v-else class="grid grid-cols-2 gap-3">
        <router-link
          v-for="p in products"
          :key="p.id"
          :to="`/m/product/${p.id}`"
          class="block bg-dark-card border border-dark-border rounded-lg overflow-hidden hover:border-gold/40 transition-all group"
        >
          <!-- Image container (square) -->
          <div class="relative aspect-square bg-dark overflow-hidden">
            <!-- Main image -->
            <img
              v-if="p.images?.[0]"
              :src="p.images[0]"
              :alt="p.title"
              loading="lazy"
              class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
            
            <!-- Placeholder feather icon when no image -->
            <div v-else class="w-full h-full flex items-center justify-center">
              <svg class="w-16 h-24 opacity-10" viewBox="0 0 60 160" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M30 4 C22 20 8 40 10 80 C13 110 22 135 30 156 C38 135 47 110 50 80 C52 40 38 20 30 4Z" fill="#C9A84C"/>
                <line x1="30" y1="4" x2="30" y2="156" stroke="#C9A84C" stroke-width="1.5"/>
              </svg>
            </div>

            <!-- Sold out overlay -->
            <div
              v-if="!p.available"
              class="absolute inset-0 bg-dark/70 flex items-center justify-center"
            >
              <span class="text-text-muted text-xs font-medium border border-dark-border px-2 py-1 rounded">
                售出
              </span>
            </div>
          </div>

          <!-- Product info (below image) -->
          <div class="p-2.5 space-y-1.5">
            <!-- Title -->
            <p class="text-text-primary text-xs leading-relaxed line-clamp-2 font-jp min-h-[2.5rem]">
              {{ p.title }}
            </p>

            <!-- Badges row (source and condition) -->
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="badge-gold text-[10px]">{{ p.source_name }}</span>
              <span v-if="p.condition" class="text-text-secondary text-[10px] px-1.5 py-0.5 border border-dark-border rounded">
                {{ p.condition }}
              </span>
            </div>

            <!-- Price + stock -->
            <div class="flex items-center justify-between">
              <span class="text-gold font-mono font-medium text-sm">
                {{ formatPrice(p.price_raw, p.price_jpy) }}
              </span>
              <span v-if="p.available" class="flex items-center gap-1 text-[10px] text-green-400">
                <span class="w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />
                有貨
              </span>
              <span v-else class="text-text-muted text-[10px]">
                售出
              </span>
            </div>

            <!-- Category badge -->
            <div v-if="p.category" class="flex items-center gap-1.5 flex-wrap">
              <span class="text-text-muted text-[10px] px-1.5 py-0.5 border border-dark-border rounded">
                {{ p.category }}
              </span>
            </div>
          </div>
        </router-link>
      </div>

      <!-- Loading more indicator -->
      <div v-if="loadingMore" class="col-span-2 text-center py-8">
        <div class="inline-flex items-center gap-2 text-text-muted text-xs">
          <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          載入更多商品...
        </div>
      </div>

      <!-- Infinite scroll trigger -->
      <div v-if="hasMore && !loadingMore" ref="loadMoreTrigger" class="col-span-2 h-1"></div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useIntersectionObserver, useScroll } from '@vueuse/core'
import { useProductStore } from '@/stores/productStore'
import { useFilterStore } from '@/stores/filterStore'
import { scrapeApi } from '@/utils/api'
import { formatPrice } from '@/utils/currency'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const productStore = useProductStore()
const filterStore = useFilterStore()

const products = computed(() => productStore.products)
const total = computed(() => productStore.total)
const loading = computed(() => productStore.loading)
const loadingMore = computed(() => productStore.loadingMore)
const hasMore = computed(() => productStore.hasMore)

// Environment variables
const allowManualSync = __ALLOW_MANUAL_SYNC__

const filterOpen = ref(false)
const syncing = ref(false)

const allSources = [
  { key: 'deltaone_jp', name: 'DeltaOne JP' },
  { key: 'deltaone_hk', name: 'DeltaOne HK' },
  { key: 'corner', name: 'Corner' },
  { key: 'nativefeather', name: 'Native Feather' },
  { key: 'truemark', name: 'TrueMark' },
  { key: 'rinkan', name: 'RINKAN' },
]

const localSources = ref([...filterStore.sources])
const localInStock = ref(filterStore.inStock !== false)
const localCategories = ref([...filterStore.categories])
const loadMoreTrigger = ref<HTMLElement | null>(null)

// Categories from store or fallback
const allCategories = computed(() => 
  productStore.categories.length 
    ? productStore.categories 
    : ['フェザー', 'イーグル', 'メタル', 'リング', 'ブレス', 'チェーン/ホイール', 'レザー', 'その他']
)

// Infinite scroll setup
useIntersectionObserver(
  loadMoreTrigger,
  ([{ isIntersecting }]) => {
    if (isIntersecting && hasMore.value && !loadingMore.value && !loading.value) {
      productStore.loadMoreProducts()
    }
  },
  { threshold: 0.1 }
)

// Reset page and products when filter changes
watch(
  () => filterStore.sources,
  () => {
    filterStore.setPage(1)
    productStore.fetchProducts(true)
  }
)

watch(
  () => filterStore.conditions,
  () => {
    filterStore.setPage(1)
    productStore.fetchProducts(true)
  }
)

watch(
  () => filterStore.categories,
  () => {
    filterStore.setPage(1)
    productStore.fetchProducts(true)
  }
)

watch(
  () => filterStore.inStock,
  () => {
    filterStore.setPage(1)
    productStore.fetchProducts(true)
  }
)

watch(
  () => filterStore.sort,
  () => {
    filterStore.setPage(1)
    productStore.fetchProducts(true)
  }
)

watch(
  () => filterStore.q,
  () => {
    filterStore.setPage(1)
    productStore.fetchProducts(true)
  }
)

async function handleSync() {
  syncing.value = true
  try {
    await scrapeApi.trigger()
    const poll = setInterval(async () => {
      const s = await scrapeApi.status()
      if (!s.running) {
        clearInterval(poll)
        syncing.value = false
        await productStore.fetchProducts(true)
      }
    }, 2000)
  } catch {
    syncing.value = false
  }
}

function applyFilter() {
  filterStore.sources = localSources.value
  filterStore.inStock = localInStock.value ? true : null
  filterStore.categories = localCategories.value
  filterStore.setPage(1)
  productStore.fetchProducts(true)
  filterOpen.value = false
}

onMounted(() => {
  productStore.fetchProducts(true)
})
</script>
