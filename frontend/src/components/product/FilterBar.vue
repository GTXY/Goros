<template>
  <div class="sticky top-14 z-40 bg-dark/95 backdrop-blur border-b border-dark-border">
    <div class="max-w-screen-2xl mx-auto px-4 py-2.5 flex items-center gap-3 flex-wrap md:flex-nowrap">

      <!-- Filter button -->
      <div class="relative" ref="filterRef">
        <button
          @click="togglePanel"
          class="flex items-center gap-1.5 border text-xs px-3 py-1.5 rounded transition-all"
          :class="activeCount > 0
            ? 'border-gold text-gold bg-gold/10'
            : 'border-dark-border text-text-secondary hover:border-gold hover:text-gold'"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M3 4h18M6 8h12M10 12h4"/>
          </svg>
          {{ activeCount > 0 ? t('filter.filterCount', { n: activeCount }) : t('filter.filter') }}
        </button>

        <!-- Filter panel -->
        <FilterPanel v-if="panelOpen" @close="panelOpen = false" />
      </div>

      <!-- Active filter chips -->
      <div class="flex items-center gap-1.5 flex-wrap flex-1">
        <span
          v-for="src in filterStore.sources"
          :key="src"
          class="inline-flex items-center gap-1 badge-gold text-[10px] cursor-pointer"
          @click="removeSource(src)"
        >
          {{ sourceLabel(src) }} <span class="opacity-60 hover:opacity-100">✕</span>
        </span>
        <span
          v-for="cat in filterStore.categories"
          :key="cat"
          class="inline-flex items-center gap-1 badge-blue text-[10px] cursor-pointer"
          @click="removeCategory(cat)"
        >
          {{ t(`categories.${cat}`, cat) }} <span class="opacity-60 hover:opacity-100">✕</span>
        </span>
        <span
          v-for="cond in filterStore.conditions"
          :key="cond"
          class="inline-flex items-center gap-1 badge-gray text-[10px] cursor-pointer"
          @click="removeCondition(cond)"
        >
          {{ t(`conditions.${cond}`, cond) }} <span class="opacity-60 hover:opacity-100">✕</span>
        </span>
      </div>

      <div class="flex items-center gap-2 ml-auto">
        <!-- Sort -->
        <select
          v-model="filterStore.sort"
          @change="onSortChange"
          class="input-dark text-xs py-1.5 pr-6 cursor-pointer min-w-[120px]"
        >
          <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">
            {{ t(`filter.sortOptions.${opt.value}`) }}
          </option>
        </select>

        <!-- Search -->
        <input
          v-model="searchInput"
          @keydown.enter="onSearch"
          @input="debouncedSearch"
          type="text"
          :placeholder="t('filter.search')"
          class="input-dark text-xs py-1.5 w-44 lg:w-56"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useFilterStore } from '@/stores/filterStore'
import { useProductStore } from '@/stores/productStore'
import FilterPanel from './FilterPanel.vue'

const { t } = useI18n()
const filterStore = useFilterStore()
const productStore = useProductStore()

const panelOpen = ref(false)
const filterRef = ref<HTMLElement | null>(null)
const searchInput = ref(filterStore.q)
let searchTimer: ReturnType<typeof setTimeout> | null = null

const activeCount = computed(() => filterStore.activeCount())

const sortOptions = [
  { value: 'scraped_at_desc' },
  { value: 'price_asc' },
  { value: 'price_desc' },
  { value: 'created_at_desc' },
]

const sourceLabels: Record<string, string> = {
  deltaone_jp: 'DeltaOne JP',
  deltaone_hk: 'DeltaOne HK',
  corner: 'Corner',
  nativefeather: 'Native Feather',
  truemark: 'TrueMark',
  rinkan: 'RINKAN',
}
const sourceLabel = (key: string) => sourceLabels[key] ?? key

function togglePanel() {
  panelOpen.value = !panelOpen.value
}

function removeSource(s: string) {
  filterStore.sources = filterStore.sources.filter(x => x !== s)
  filterStore.setPage(1)
  productStore.fetchProducts()
}

function removeCategory(c: string) {
  filterStore.categories = filterStore.categories.filter(x => x !== c)
  filterStore.setPage(1)
  productStore.fetchProducts()
}

function removeCondition(c: string) {
  filterStore.conditions = filterStore.conditions.filter(x => x !== c)
  filterStore.setPage(1)
  productStore.fetchProducts()
}

function onSortChange() {
  filterStore.setPage(1)
  productStore.fetchProducts()
}

function onSearch() {
  filterStore.q = searchInput.value
  filterStore.setPage(1)
  productStore.fetchProducts()
}

function debouncedSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(onSearch, 500)
}

// 关闭面板（点击外部）
function onClickOutside(e: MouseEvent) {
  if (panelOpen.value && filterRef.value && !filterRef.value.contains(e.target as Node)) {
    panelOpen.value = false
  }
}
document.addEventListener('click', onClickOutside)
</script>
