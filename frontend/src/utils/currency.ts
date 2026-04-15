import type { ExchangeRates } from '@/stores/ratesStore'

/** 价格是否为询价（ASK） */
export function isAskPrice(priceJpy: number | null | undefined, priceRaw: string | null | undefined): boolean {
  if (priceRaw === 'ASK') return true
  if (priceJpy == null || priceJpy === 0) return true
  return false
}

export function formatJPY(amount: number): string {
  return `¥${amount.toLocaleString('ja-JP')}`
}

export function formatCNY(amount: number): string {
  return `¥${amount.toLocaleString('zh-CN')}`
}

/**
 * 根据当前语言环境格式化价格。
 * - ja：显示日元
 * - zh-TW：将日元换算为人民币后显示
 * - 询价商品始终返回 'ASK'
 */
export function formatPriceByLocale(
  priceJpy: number | null | undefined,
  priceRaw: string | null | undefined,
  locale: string,
  rates: ExchangeRates,
): string {
  if (isAskPrice(priceJpy, priceRaw)) return 'ASK'
  if (!priceJpy) return '—'

  if (locale === 'zh-TW') {
    const cny = Math.round(priceJpy * rates.JPY_TO_CNY)
    return formatCNY(cny)
  }
  return formatJPY(priceJpy)
}

/** 当前语言对应的货币标签 */
export function currencyLabel(locale: string): string {
  return locale === 'zh-TW' ? 'CNY' : 'JPY'
}

// 向下兼容旧调用（MobileListView / MobileDetailView）
export function formatPrice(raw: string | null, priceJpy: number | null, _currency?: string): string {
  if (isAskPrice(priceJpy, raw)) return 'ASK'
  if (priceJpy != null && priceJpy > 0) return formatJPY(priceJpy)
  if (raw) return raw
  return '—'
}
