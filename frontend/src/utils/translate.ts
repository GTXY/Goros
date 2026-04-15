/**
 * 基于 Google Translate 免费接口的翻译工具（无需 API Key）。
 * 结果持久化到 localStorage，避免重复请求。
 */

const CACHE_KEY = 'goros_t9n_v1'
const CACHE_MAX = 2000

// 内存缓存
const mem = new Map<string, string>()

// 启动时从 localStorage 加载
try {
  const raw = localStorage.getItem(CACHE_KEY)
  if (raw) {
    const obj = JSON.parse(raw) as Record<string, string>
    Object.entries(obj).forEach(([k, v]) => mem.set(k, v))
  }
} catch { /* ignore */ }

function persist() {
  try {
    if (mem.size > CACHE_MAX) {
      // 超量时清掉最早的一半
      const entries = [...mem.entries()].slice(Math.floor(CACHE_MAX / 2))
      mem.clear()
      entries.forEach(([k, v]) => mem.set(k, v))
    }
    localStorage.setItem(CACHE_KEY, JSON.stringify(Object.fromEntries(mem)))
  } catch { /* ignore */ }
}

/**
 * 将文本翻译到目标语言。
 * @param text  原文（日文或英文）
 * @param to    目标语言代码，'zh-TW' 或 'ja'
 */
export async function translate(text: string, to: string): Promise<string> {
  if (!text?.trim()) return text

  const key = `${to}|${text}`
  if (mem.has(key)) return mem.get(key)!

  try {
    const url = new URL('https://translate.googleapis.com/translate_a/single')
    url.searchParams.set('client', 'gtx')
    url.searchParams.set('sl', 'auto')
    url.searchParams.set('tl', to)
    url.searchParams.set('dt', 't')
    url.searchParams.set('q', text)

    const res = await fetch(url.toString())
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()

    // 格式: [[[["翻訳","原文",...],...],...], null, "detected"]
    const segments: string = (data[0] as Array<[string]>)
      ?.map(s => s[0])
      .filter(Boolean)
      .join('') || text

    mem.set(key, segments)
    persist()
    return segments
  } catch {
    return text
  }
}

