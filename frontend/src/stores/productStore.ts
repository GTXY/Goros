import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Product, ProductListResponse, StatsResponse } from '@/types'
import { productApi } from '@/utils/api'
import { useFilterStore } from './filterStore'

export const useProductStore = defineStore('product', () => {
  const products = ref<Product[]>([])
  const total = ref(0)
  const pages = ref(1)
  const currentPage = ref(1)
  const loading = ref(false)
  const loadingMore = ref(false)
  const error = ref<string | null>(null)
  const stats = ref<StatsResponse | null>(null)
  const categories = ref<string[]>([])
  const hasMore = ref(true)

  async function fetchProducts(reset = true) {
    const filterStore = useFilterStore()
    
    // Reset state if fetching fresh
    if (reset) {
      products.value = []
      currentPage.value = 1
      hasMore.value = true
    }
    
    loading.value = true
    error.value = null
    try {
      const params = filterStore.toParams()
      const res = await productApi.list(params)
      
      if (reset) {
        products.value = res.products
      } else {
        // Append new products
        products.value = [...products.value, ...res.products]
      }
      
      total.value = res.total
      pages.value = res.pages
      
      // Update hasMore flag
      if (reset) {
        hasMore.value = res.products.length > 0 && res.page < res.pages
      } else {
        hasMore.value = res.page < res.pages
      }
      
      // Update current page
      currentPage.value = res.page
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '請求失敗'
    } finally {
      loading.value = false
    }
  }

  async function loadMoreProducts() {
    if (loadingMore.value || !hasMore.value) return
    
    const filterStore = useFilterStore()
    loadingMore.value = true
    
    try {
      // Increment page for next request
      const nextPage = currentPage.value + 1
      filterStore.setPage(nextPage)
      
      const params = filterStore.toParams()
      const res = await productApi.list(params)
      
      // Append new products
      products.value = [...products.value, ...res.products]
      hasMore.value = res.page < res.pages
      currentPage.value = res.page
    } catch (e: unknown) {
      console.error('Failed to load more products:', e)
    } finally {
      loadingMore.value = false
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

  return { 
    products, 
    total, 
    pages, 
    currentPage,
    loading, 
    loadingMore,
    hasMore,
    error, 
    stats, 
    categories, 
    fetchProducts, 
    fetchStats, 
    fetchCategories,
    loadMoreProducts
  }
})
