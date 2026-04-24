<template>
  <div class="min-h-screen pb-6">
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-dark/95 backdrop-blur border-b border-dark-border px-4 h-12 flex items-center gap-3">
      <router-link to="/m/" class="text-text-muted hover:text-gold transition-colors">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </router-link>
      <div class="flex items-center gap-1">
        <img src="/goros-feather.png" class="h-5 w-auto" alt="GOROS Logo" />
        <span class="text-gold font-bold font-mono tracking-widest text-sm">GOROS</span>
      </div>
    </header>

    <LoadingSpinner v-if="loading" />
    <div v-else-if="error" class="text-center py-20 text-text-muted text-sm px-4">{{ error }}</div>

    <div v-else-if="product">
      <!-- Image -->
      <div class="relative aspect-square bg-dark">
        <img
          v-if="product.images?.[0]"
          :src="activeImg"
          :alt="product.title"
          class="w-full h-full object-contain p-4"
        />
        <div v-else class="w-full h-full flex items-center justify-center">
          <img src="/feather-watermark.svg" class="w-20 h-28 opacity-10" alt="" />
        </div>
      </div>

      <!-- Thumbnails -->
      <div v-if="product.images?.length > 1" class="flex gap-2 overflow-x-auto px-4 py-2">
        <button
          v-for="(img, i) in product.images"
          :key="i"
          @click="activeIdx = i"
          class="flex-shrink-0 w-12 h-12 rounded border-2 overflow-hidden"
          :class="i === activeIdx ? 'border-gold' : 'border-dark-border'"
        >
          <img :src="img" class="w-full h-full object-contain" />
        </button>
      </div>

      <!-- Info -->
      <div class="px-4 py-4 space-y-4">
        <div class="flex items-center gap-2">
          <span class="badge-gold text-xs">{{ product.source_name }}</span>
          <span class="w-2 h-2 rounded-full" :class="product.available ? 'bg-green-400' : 'bg-text-muted'" />
          <span class="text-xs" :class="product.available ? 'text-green-400' : 'text-text-muted'">
            {{ product.available ? '有貨' : '已售出' }}
          </span>
        </div>

        <h1 class="text-text-primary text-base font-medium leading-snug font-jp">
          {{ product.title }}
        </h1>

        <div>
          <div class="text-gold font-mono text-3xl font-bold">
            {{ displayPrice }}
          </div>
          <span v-if="displayPrice !== 'ASK'" class="text-text-muted text-xs ml-1">JPY</span>
        </div>

        <div v-if="product.description" class="bg-dark-card border border-dark-border rounded-lg p-3">
          <p class="text-text-muted text-xs mb-1.5 font-semibold">商品說明</p>
          <p class="text-text-secondary text-xs leading-relaxed whitespace-pre-line font-jp">
            {{ product.description }}
          </p>
        </div>

        <a
          v-if="product.url"
          :href="product.url"
          target="_blank"
          rel="noopener noreferrer"
          class="btn-gold w-full text-center block py-3 text-sm"
        >
          前往 {{ product.source_name }} 購買 →
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import type { Product } from '@/types'
import { productApi } from '@/utils/api'
import { formatPrice } from '@/utils/currency'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const route = useRoute()
const product = ref<Product | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const activeIdx = ref(0)
const activeImg = computed(() => product.value?.images?.[activeIdx.value] ?? '')
const displayPrice = computed(() =>
  product.value ? formatPrice(product.value.price_raw, product.value.price_jpy) : '—'
)

onMounted(async () => {
  try {
    product.value = await productApi.get(Number(route.params.id))
  } catch {
    error.value = '商品不存在或載入失敗'
  } finally {
    loading.value = false
  }
})
</script>
