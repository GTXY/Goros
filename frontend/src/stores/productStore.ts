import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Product, ProductListResponse, StatsResponse } from '@/types'
import { productApi } from '@/utils/api'
import { useFilterStore } from './filterStore'

export const useProductStore = defineStore('product', () => {
  const products = ref<Product[]>([])
  const total = ref(0)
  const pages = ref(1)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const stats = ref<StatsResponse | null>(null)
  const categories = ref<string[]>([])

  async function fetchProducts() {
    const filterStore = useFilterStore()
    loading.value = true
    error.value = null
    try {
      const res = await productApi.list(filterStore.toParams())
      products.value = res.products
      total.value = res.total
      pages.value = res.pages
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '請求失敗'
    } finally {
      loading.value = false
    }
  }

  async function fetchStats() {
    try {
      stats.value = await productApi.stats()
    } catch { /* silent */ }
  }

  async function fetchCategories() {
    try {
      const res = await productApi.categories()
      categories.value = res.categories
    } catch { /* silent */ }
  }

  return { products, total, pages, loading, error, stats, categories, fetchProducts, fetchStats, fetchCategories }
})
