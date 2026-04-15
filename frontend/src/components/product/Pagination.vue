<template>
  <div v-if="pages > 1" class="flex items-center justify-center gap-1.5 py-8">
    <button
      @click="goTo(current - 1)"
      :disabled="current <= 1"
      class="w-8 h-8 flex items-center justify-center rounded text-xs text-text-secondary border border-dark-border hover:border-gold hover:text-gold transition-all disabled:opacity-30 disabled:cursor-not-allowed"
    >‹</button>

    <template v-for="p in pageList" :key="p">
      <span v-if="p === '...'" class="w-8 h-8 flex items-center justify-center text-text-muted text-xs">…</span>
      <button
        v-else
        @click="goTo(Number(p))"
        class="w-8 h-8 flex items-center justify-center rounded text-xs transition-all border"
        :class="Number(p) === current
          ? 'bg-gold text-dark border-gold font-semibold'
          : 'border-dark-border text-text-secondary hover:border-gold hover:text-gold'"
      >{{ p }}</button>
    </template>

    <button
      @click="goTo(current + 1)"
      :disabled="current >= pages"
      class="w-8 h-8 flex items-center justify-center rounded text-xs text-text-secondary border border-dark-border hover:border-gold hover:text-gold transition-all disabled:opacity-30 disabled:cursor-not-allowed"
    >›</button>

    <span class="text-xs text-text-muted ml-3">
      {{ t('page.total', { total: total.toLocaleString(), page: current, pages }) }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const props = defineProps<{ current: number; pages: number; total: number }>()
const emit = defineEmits<{ (e: 'change', page: number): void }>()

function goTo(p: number) {
  if (p < 1 || p > props.pages) return
  emit('change', p)
}

const pageList = computed(() => {
  const { current, pages } = props
  if (pages <= 7) return Array.from({ length: pages }, (_, i) => i + 1)
  const items: (number | string)[] = [1]
  if (current > 3) items.push('...')
  for (let i = Math.max(2, current - 1); i <= Math.min(pages - 1, current + 1); i++) {
    items.push(i)
  }
  if (current < pages - 2) items.push('...')
  items.push(pages)
  return items
})
</script>
