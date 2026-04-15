import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FilterState } from '@/types'

export const useFilterStore = defineStore('filter', () => {
  const sources = ref<string[]>([])
  const conditions = ref<string[]>([])
  const categories = ref<string[]>([])
  const inStock = ref<boolean | null>(true)
  const sort = ref('scraped_at_desc')
  const q = ref('')
  const page = ref(1)

  function reset() {
    sources.value = []
    conditions.value = []
    categories.value = []
    inStock.value = true
    sort.value = 'scraped_at_desc'
    q.value = ''
    page.value = 1
  }

  function setPage(p: number) {
    page.value = p
  }

  function toParams() {
    return {
      page: page.value,
      limit: 24,
      source: sources.value.length ? sources.value.join(',') : undefined,
      condition: conditions.value.length ? conditions.value.join(',') : undefined,
      category: categories.value.length ? categories.value.join(',') : undefined,
      in_stock: inStock.value,
      sort: sort.value,
      q: q.value || undefined,
    }
  }

  function activeCount() {
    let n = 0
    if (sources.value.length) n++
    if (conditions.value.length) n++
    if (categories.value.length) n++
    if (inStock.value === false) n++
    if (q.value) n++
    return n
  }

  return { sources, conditions, categories, inStock, sort, q, page, reset, setPage, toParams, activeCount }
})
