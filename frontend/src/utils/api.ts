import axios from 'axios'
import type { ProductListResponse, Product, StatsResponse, ScrapeStatus } from '@/types'

const api = axios.create({
  baseURL: '/Goros/api',
  timeout: 30000,
})

export const productApi = {
  list(params: {
    page?: number
    limit?: number
    source?: string
    condition?: string
    category?: string
    in_stock?: boolean | null
    sort?: string
    q?: string
  }): Promise<ProductListResponse> {
    const cleaned: Record<string, unknown> = {}
    for (const [k, v] of Object.entries(params)) {
      if (v !== null && v !== undefined && v !== '') {
        cleaned[k] = v
      }
    }
    return api.get('/products', { params: cleaned }).then(r => r.data)
  },

  get(id: number): Promise<Product> {
    return api.get(`/products/${id}`).then(r => r.data)
  },

  stats(): Promise<StatsResponse> {
    return api.get('/products/stats').then(r => r.data)
  },

  categories(): Promise<{ categories: string[] }> {
    return api.get('/products/categories').then(r => r.data)
  },
}

export const scrapeApi = {
  trigger(): Promise<{ message: string; running: boolean }> {
    return api.post('/scrape/all').then(r => r.data)
  },

  status(): Promise<ScrapeStatus> {
    return api.get('/scrape/status').then(r => r.data)
  },
}

export const ratesApi = {
  get(): Promise<{ JPY_TO_CNY: number; JPY_TO_USD: number; JPY_TO_HKD: number; date: string }> {
    return api.get('/products/rates').then(r => r.data)
  },
}
