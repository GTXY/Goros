<template>
  <div class="border-t border-dark-border bg-dark-card/80 backdrop-blur">
    <div class="max-w-screen-2xl mx-auto px-4 py-3">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs font-semibold text-text-secondary uppercase tracking-wider">
          {{ t('scrape.title') }}
        </span>
        <button @click="$emit('close')" class="text-text-muted hover:text-text-primary text-xs">✕</button>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2">
        <div
          v-for="source in allSources"
          :key="source.key"
          class="flex items-center gap-1.5 text-xs"
        >
          <span class="w-2 h-2 rounded-full flex-shrink-0" :class="getStatusColor(source.key)" />
          <span class="text-text-secondary truncate">{{ source.name }}</span>
          <span v-if="getResult(source.key)" class="text-text-muted ml-1 whitespace-nowrap">
            {{ getResultText(source.key) }}
          </span>
        </div>
      </div>

      <!-- 进度条 -->
      <div class="mt-3 h-0.5 bg-dark-border rounded-full overflow-hidden">
        <div
          class="h-full bg-gold rounded-full transition-all duration-500"
          :style="{ width: progressPct + '%' }"
        />
      </div>

      <!-- 完成提示 -->
      <div v-if="isDone" class="mt-2 text-xs text-gold">
        {{ t('scrape.done', { total: totalCount }) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ScrapeStatus } from '@/types'

const { t } = useI18n()
const props = defineProps<{ status: ScrapeStatus | null }>()
defineEmits(['close'])

const allSources = [
  { key: 'deltaone_jp', name: 'DeltaOne JP' },
  { key: 'deltaone_hk', name: 'DeltaOne HK' },
  { key: 'corner', name: 'Corner' },
  { key: 'nativefeather', name: 'Native Feather' },
  { key: 'truemark', name: 'TrueMark' },
  { key: 'fivesix', name: 'FiveSix' },
  { key: 'rinkan', name: 'RINKAN' },
]

const getResult = (key: string) => props.status?.results?.find(r => r.source === key)

const getStatusColor = (key: string) => {
  const r = getResult(key)
  if (!r) return props.status?.running ? 'bg-text-muted animate-pulse' : 'bg-dark-border'
  if (r.status === 'success') return 'bg-green-500'
  if (r.status === 'failed') return 'bg-red-500'
  return 'bg-yellow-500'
}

const getResultText = (key: string) => {
  const r = getResult(key)
  if (!r) return ''
  if (r.status === 'success') return t('scrape.success', { count: r.count })
  if (r.status === 'failed') return t('scrape.failed')
  return t('scrape.skipped')
}

const progressPct = computed(() => {
  if (!props.status) return 0
  const { total_sources, completed_sources } = props.status
  return total_sources > 0 ? Math.round((completed_sources / total_sources) * 100) : 0
})

const isDone = computed(() => props.status && !props.status.running && props.status.completed_sources > 0)

const totalCount = computed(() => props.status?.results?.reduce((s, r) => s + r.count, 0) ?? 0)
</script>
