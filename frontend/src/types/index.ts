export interface Product {
  id: number
  source: string
  source_name: string
  source_id: string
  title: string
  price_raw: string | null
  price_jpy: number | null
  currency: string
  condition: string | null
  category: string | null
  images: string[]
  url: string | null
  available: boolean
  tags: string[]
  description: string | null
  scraped_at: string | null
  created_at: string | null
}

export interface ProductListResponse {
  products: Product[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface SourceStats {
  source: string
  name: string
  count: number
  available_count: number
  last_scraped: string | null
}

export interface CategoryStats {
  name: string
  count: number
}

export interface StatsResponse {
  total_products: number
  available_products: number
  sources: SourceStats[]
  categories: CategoryStats[]
  last_scrape: string | null
}

export interface ScrapeResult {
  source: string
  name: string
  status: 'success' | 'failed' | 'skipped'
  count: number
  error: string | null
}

export interface ScrapeStatus {
  running: boolean
  started_at: string | null
  finished_at: string | null
  total_sources: number
  completed_sources: number
  results: ScrapeResult[]
}

export interface FilterState {
  sources: string[]
  conditions: string[]
  categories: string[]
  inStock: boolean | null
  sort: string
  q: string
  page: number
}

export type SortOption = {
  value: string
  labelKey: string
}
