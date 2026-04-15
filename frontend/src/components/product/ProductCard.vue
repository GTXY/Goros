<template>
  <router-link
    :to="`/product/${product.id}`"
    class="card group block"
  >
    <!-- Image -->
    <div class="relative aspect-square bg-dark overflow-hidden">
      <img
        v-if="mainImage"
        :src="mainImage"
        :alt="product.title"
        loading="lazy"
        class="w-full h-full object-contain p-2 transition-transform duration-300 group-hover:scale-105"
        @error="imgError = true"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <svg class="w-16 h-24 opacity-10" viewBox="0 0 60 160" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M30 4 C22 20 8 40 10 80 C13 110 22 135 30 156 C38 135 47 110 50 80 C52 40 38 20 30 4Z" fill="#C9A84C"/>
          <line x1="30" y1="4" x2="30" y2="156" stroke="#C9A84C" stroke-width="1.5"/>
        </svg>
      </div>

      <!-- Sold out overlay -->
      <div
        v-if="!product.available"
        class="absolute inset-0 bg-dark/70 flex items-center justify-center"
      >
        <span class="text-text-muted text-sm font-medium border border-dark-border px-3 py-1 rounded">
          {{ t('product.soldOut') }}
        </span>
      </div>
    </div>

    <!-- Info -->
    <div class="p-3 space-y-1.5">
      <!-- Title: 显示翻译后标题，加载时显示原标题 -->
      <p class="text-text-primary text-xs leading-relaxed line-clamp-2 font-jp min-h-[2.5rem]"
         :class="{ 'opacity-60': isTranslating }">
        {{ displayTitle }}
      </p>

      <!-- Badges row -->
      <div class="flex items-center gap-1.5 flex-wrap">
        <span class="badge-gold text-[10px]">{{ product.source_name }}</span>
        <span v-if="product.condition" :class="conditionClass" class="text-[10px]">
          {{ t(`conditions.${product.condition}`, product.condition) }}
        </span>
      </div>

      <!-- Price + stock -->
      <div class="flex items-center justify-between">
        <span class="text-gold font-mono font-medium text-sm">
          {{ displayPrice }}
          <span v-if="displayPrice !== 'ASK'" class="text-text-muted text-[10px] font-sans ml-0.5">{{ priceCurrencyLabel }}</span>
        </span>
        <span v-if="product.available" class="flex items-center gap-1 text-[10px] text-green-400">
          <span class="w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />
          {{ t('product.available') }}
        </span>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Product } from '@/types'
import { formatPriceByLocale, currencyLabel } from '@/utils/currency'
import { translate } from '@/utils/translate'
import { useRatesStore } from '@/stores/ratesStore'

const props = defineProps<{ product: Product }>()
const { t, locale } = useI18n()
const imgError = ref(false)
const ratesStore = useRatesStore()

const displayPrice = computed(() =>
  formatPriceByLocale(props.product.price_jpy, props.product.price_raw, locale.value, ratesStore.rates)
)
const priceCurrencyLabel = computed(() => currencyLabel(locale.value))

const mainImage = computed(() => {
  if (imgError.value || !props.product.images?.length) return null
  return props.product.images[0]
})

const conditionClass = computed(() => {
  const c = props.product.condition
  if (!c) return 'badge-gray'
  if (['新品', 'ほぼ新品'].includes(c)) return 'badge-green'
  if (['超美品', '美品', '美中古'].includes(c)) return 'badge-blue'
  return 'badge-gray'
})

// ----- 标题翻译 -----
const translatedTitle = ref(props.product.title)
const isTranslating = ref(false)

const displayTitle = computed(() => translatedTitle.value || props.product.title)

async function refreshTitle(lang: string) {
  isTranslating.value = true
  translatedTitle.value = await translate(props.product.title, lang)
  isTranslating.value = false
}

watch(
  locale,
  (lang) => refreshTitle(lang),
  { immediate: true }
)
</script>
