import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ratesApi } from '@/utils/api'

export interface ExchangeRates {
  JPY_TO_CNY: number
  JPY_TO_USD: number
  JPY_TO_HKD: number
  date: string
}

const DEFAULTS: ExchangeRates = {
  JPY_TO_CNY: 0.0474,
  JPY_TO_USD: 0.0067,
  JPY_TO_HKD: 0.054,
  date: 'fallback',
}

export const useRatesStore = defineStore('rates', () => {
  const rates = ref<ExchangeRates>({ ...DEFAULTS })
  const loaded = ref(false)

  async function fetchRates() {
    try {
      const data = await ratesApi.get()
      rates.value = data
    } catch {
      // 保持默认汇率
    } finally {
      loaded.value = true
    }
  }

  return { rates, loaded, fetchRates }
})
