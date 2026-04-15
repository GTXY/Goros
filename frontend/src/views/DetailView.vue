<template>
  <div class="min-h-screen">
    <AppHeader />

    <main class="max-w-screen-xl mx-auto px-4 py-6">
      <!-- Breadcrumb -->
      <nav class="text-xs text-text-muted mb-6 flex items-center gap-1.5">
        <router-link to="/" class="hover:text-gold transition-colors">{{ t('breadcrumb.home') }}</router-link>
        <span>›</span>
        <span class="text-text-secondary">{{ t('breadcrumb.detail') }}</span>
      </nav>

      <LoadingSpinner v-if="loading" />
      <ErrorState v-else-if="error" :message="error" :retry="true" @retry="load()" />

      <div v-else-if="product" class="grid grid-cols-1 lg:grid-cols-[1fr_45%] gap-8 xl:gap-12">
        <!-- Left: Image carousel -->
        <div>
          <ImageCarousel :images="product.images" :alt="product.title" />
        </div>

        <!-- Right: Info -->
        <div class="space-y-5">
          <!-- Source badge -->
          <div>
            <a
              v-if="product.url"
              :href="product.url"
              target="_blank"
              rel="noopener noreferrer"
              class="badge-gold text-xs inline-flex items-center gap-1 hover:bg-gold/30 transition-colors"
            >
              {{ product.source_name }}
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
              </svg>
            </a>
            <span v-else class="badge-gold text-xs">{{ product.source_name }}</span>
          </div>

          <!-- Title（与 UI 语言一致，自动翻译）-->
          <h1 class="text-text-primary text-xl font-medium leading-snug font-jp"
              :class="{ 'opacity-50': isTranslating }">
            {{ displayTitle }}
          </h1>

          <!-- Tags -->
          <div class="flex flex-wrap gap-1.5">
            <span v-if="product.condition" :class="conditionClass">
              {{ t(`conditions.${product.condition}`, product.condition) }}
            </span>
            <span v-for="tag in displayTags" :key="tag" class="badge-gray text-xs">{{ tag }}</span>
          </div>

          <!-- Price -->
          <div>
            <div class="flex items-baseline gap-2">
              <span class="text-gold font-mono text-4xl font-bold">
                {{ displayPrice }}
              </span>
              <span v-if="displayPrice !== 'ASK'" class="text-text-muted text-sm">{{ priceCurrencyLabel }}</span>
            </div>
          </div>

          <!-- Divider -->
          <div class="border-t border-dark-border" />

          <!-- Info grid -->
          <div class="grid grid-cols-3 gap-4">
            <div>
              <p class="text-text-muted text-xs mb-1">{{ t('product.source') }}</p>
              <a
                v-if="product.url"
                :href="product.url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-text-primary text-sm hover:text-gold transition-colors flex items-center gap-1"
              >
                {{ product.source_name }}
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                </svg>
              </a>
              <span v-else class="text-text-primary text-sm">{{ product.source_name }}</span>
            </div>
            <div>
              <p class="text-text-muted text-xs mb-1">{{ t('product.lastUpdated') }}</p>
              <p class="text-text-primary text-sm">{{ formatDate(product.scraped_at) }}</p>
            </div>
            <div>
              <p class="text-text-muted text-xs mb-1">{{ t('product.stockStatus') }}</p>
              <div class="flex items-center gap-1.5">
                <span
                  class="w-2 h-2 rounded-full"
                  :class="product.available ? 'bg-green-400' : 'bg-text-muted'"
                />
                <span class="text-sm" :class="product.available ? 'text-green-400' : 'text-text-muted'">
                  {{ product.available ? t('product.available') : t('product.soldOut') }}
                </span>
              </div>
            </div>
          </div>

          <!-- Description（与 UI 语言一致，自动翻译）-->
          <div v-if="displayDesc" class="bg-dark-card border border-dark-border rounded-lg p-4">
            <p class="text-text-muted text-xs mb-2 font-semibold uppercase tracking-wider">
              {{ t('product.description') }}
            </p>
            <p class="text-text-secondary text-sm leading-relaxed whitespace-pre-line font-jp"
               :class="{ 'opacity-50': isTranslating }">
              {{ displayDesc }}
            </p>
          </div>

          <!-- CTA buttons -->
          <div class="space-y-2 pt-2">
            <a
              v-if="product.url"
              :href="product.url"
              target="_blank"
              rel="noopener noreferrer"
              class="btn-gold w-full text-center block py-3 text-sm"
            >
              {{ t('product.viewSource', { name: product.source_name }) }} →
            </a>
            <router-link to="/" class="btn-outline w-full text-center block py-3 text-sm">
              {{ t('product.backToList') }}
            </router-link>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { Product } from '@/types'
import { productApi } from '@/utils/api'
import { formatPriceByLocale, currencyLabel } from '@/utils/currency'
import { translate } from '@/utils/translate'
import { useRatesStore } from '@/stores/ratesStore'
import AppHeader from '@/components/common/AppHeader.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import ImageCarousel from '@/components/product/ImageCarousel.vue'

const { t, locale } = useI18n()
const route = useRoute()
const ratesStore = useRatesStore()

const product = ref<Product | null>(null)

const displayPrice = computed(() =>
  product.value
    ? formatPriceByLocale(product.value.price_jpy, product.value.price_raw, locale.value, ratesStore.rates)
    : '—'
)
const priceCurrencyLabel = computed(() => currencyLabel(locale.value))
const loading = ref(true)
const error = ref<string | null>(null)

// ---- 翻译状态（标题 + 说明共用同一个 loading 状态）----
const translatedTitle = ref('')
const translatedDesc  = ref('')
const isTranslating   = ref(false)

const displayTitle = computed(() => translatedTitle.value || product.value?.title || '')
const displayDesc  = computed(() => translatedDesc.value  || product.value?.description || '')

/** 同时翻译标题和说明，与当前 UI 语言保持一致 */
async function translateContent(lang: string) {
  const p = product.value
  if (!p) return
  isTranslating.value = true
  try {
    const [title, desc] = await Promise.all([
      translate(p.title, lang),
      p.description ? translate(p.description, lang) : Promise.resolve(''),
    ])
    translatedTitle.value = title
    translatedDesc.value  = desc
  } finally {
    isTranslating.value = false
  }
}

// 语言切换时重新翻译
watch(locale, (lang) => translateContent(lang))

// ---- 其他 ----
const conditionClass = computed(() => {
  const c = product.value?.condition
  if (!c) return 'badge-gray text-xs'
  if (['新品', 'ほぼ新品'].includes(c)) return 'badge-green text-xs'
  if (['超美品', '美品', '美中古'].includes(c)) return 'badge-blue text-xs'
  return 'badge-gray text-xs'
})

const displayTags = computed(() => {
  const conditionTags = new Set(['新品', 'ほぼ新品', '超美品', '美品', '美中古', '中古', '不明', 'used'])
  return (product.value?.tags ?? []).filter(tag => !conditionTags.has(tag)).slice(0, 5)
})

function formatDate(dt: string | null) {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString('zh-TW')
}

async function load() {
  loading.value = true
  error.value = null
  translatedTitle.value = ''
  translatedDesc.value  = ''
  try {
    product.value = await productApi.get(Number(route.params.id))
    await translateContent(locale.value)
  } catch {
    error.value = '商品不存在或載入失敗'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
