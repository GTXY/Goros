<template>
  <div class="min-h-screen">
    <AppHeader />
    <FilterBar />

    <main class="max-w-screen-2xl mx-auto px-4 py-6">
      <!-- Empty state: no data at all -->
      <div v-if="!loading && !error && total === 0 && !hasFilters" class="flex flex-col items-center justify-center py-32 text-center">
        <img src="/feather-watermark.svg" class="w-16 h-24 opacity-20 mb-6" alt="" />
        <h2 class="text-text-primary text-lg font-medium mb-2">{{ t('empty.title') }}</h2>
        <p class="text-text-muted text-sm max-w-xs">{{ t('empty.desc') }}</p>
      </div>

      <!-- Empty state: filters returned nothing -->
      <div v-else-if="!loading && !error && total === 0 && hasFilters" class="flex flex-col items-center justify-center py-24 text-center">
        <p class="text-text-secondary text-base mb-1">{{ t('empty.noResult') }}</p>
        <p class="text-text-muted text-sm">{{ t('empty.noResultDesc') }}</p>
      </div>

      <!-- Error -->
      <ErrorState v-else-if="error" :message="error" :retry="true" @retry="productStore.fetchProducts()" />

      <!-- Loading -->
      <LoadingSpinner v-else-if="loading" />

      <!-- Products -->
      <template v-else>
        <ProductGrid :products="products" />
        <Pagination
          :current="filterStore.page"
          :pages="pages"
          :total="total"
          @change="onPageChange"
        />
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useProductStore } from '@/stores/productStore'
import { useFilterStore } from '@/stores/filterStore'
import AppHeader from '@/components/common/AppHeader.vue'
import FilterBar from '@/components/product/FilterBar.vue'
import ProductGrid from '@/components/product/ProductGrid.vue'
import Pagination from '@/components/product/Pagination.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ErrorState from '@/components/common/ErrorState.vue'

const { t } = useI18n()
const productStore = useProductStore()
const filterStore = useFilterStore()

const products = computed(() => productStore.products)
const total = computed(() => productStore.total)
const pages = computed(() => productStore.pages)
const loading = computed(() => productStore.loading)
const error = computed(() => productStore.error)
const hasFilters = computed(() => filterStore.activeCount() > 0)

function onPageChange(p: number) {
  filterStore.setPage(p)
  productStore.fetchProducts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(async () => {
  await Promise.all([
    productStore.fetchProducts(),
    productStore.fetchStats(),
    productStore.fetchCategories(),
  ])
})
</script>
