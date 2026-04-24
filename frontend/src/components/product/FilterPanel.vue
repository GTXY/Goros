<template>
  <div
    class="absolute top-full left-0 mt-1 w-[480px] max-w-[95vw] bg-dark-card border border-dark-border rounded-lg shadow-2xl shadow-black/50 z-50 p-5"
    @click.stop
  >
    <div class="grid grid-cols-2 gap-5">
      <!-- 来源平台 -->
      <div>
        <p class="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
          {{ t('filter.sources') }}
        </p>
        <div class="space-y-1.5">
          <label
            v-for="s in allSources"
            :key="s.key"
            class="flex items-center gap-2 cursor-pointer group"
          >
            <input
              type="checkbox"
              :value="s.key"
              v-model="localSources"
              class="accent-gold"
            />
            <span class="text-xs text-text-secondary group-hover:text-text-primary transition-colors">
              {{ s.name }}
            </span>
          </label>
        </div>
      </div>

      <!-- 品类 -->
      <div>
        <p class="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
          {{ t('filter.categories') }}
        </p>
        <div class="space-y-1.5">
          <label
            v-for="cat in availableCategories"
            :key="cat"
            class="flex items-center gap-2 cursor-pointer group"
          >
            <input
              type="checkbox"
              :value="cat"
              v-model="localCategories"
              class="accent-gold"
            />
            <span class="text-xs text-text-secondary group-hover:text-text-primary transition-colors">
              {{ t(`categories.${cat}`, cat) }}
            </span>
          </label>
        </div>
      </div>

      <!-- 成色 -->
      <div>
        <p class="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
          {{ t('filter.conditions') }}
        </p>
        <div class="space-y-1.5">
          <label
            v-for="c in allConditions"
            :key="c"
            class="flex items-center gap-2 cursor-pointer group"
          >
            <input
              type="checkbox"
              :value="c"
              v-model="localConditions"
              class="accent-gold"
            />
            <span class="text-xs text-text-secondary group-hover:text-text-primary transition-colors">
              {{ t(`conditions.${c}`, c) }}
            </span>
          </label>
        </div>
      </div>

      <!-- 在库状态 -->
      <div>
        <p class="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
          {{ t('filter.inStock') }}
        </p>
        <label class="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" v-model="localInStock" class="accent-gold" />
          <span class="text-xs text-text-secondary">{{ t('filter.inStockOnly') }}</span>
        </label>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center justify-between mt-5 pt-4 border-t border-dark-border">
      <button @click="reset" class="text-xs text-text-muted hover:text-text-primary transition-colors">
        {{ t('filter.reset') }}
      </button>
      <button @click="apply" class="btn-gold text-xs py-1.5 px-4">
        {{ t('filter.apply') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useFilterStore } from '@/stores/filterStore'
import { useProductStore } from '@/stores/productStore'

const { t } = useI18n()
const filterStore = useFilterStore()
const productStore = useProductStore()
const emit = defineEmits(['close'])

const allSources = [
  { key: 'deltaone_jp', name: 'DeltaOne JP' },
  { key: 'deltaone_hk', name: 'DeltaOne HK' },
  { key: 'corner', name: 'Corner' },
  { key: 'nativefeather', name: 'Native Feather' },
  { key: 'truemark', name: 'TrueMark' },
  { key: 'rinkan', name: 'RINKAN' },
]

const allConditions = ['新品', 'ほぼ新品', '超美品', '美品', '美中古', '中古']

const availableCategories = computed(() => productStore.categories.length
  ? productStore.categories
  : ['フェザー', 'イーグル', 'メタル', 'リング', 'ブレス', 'チェーン/ホイール', 'レザー', 'その他']
)

import { computed } from 'vue'

const localSources = ref([...filterStore.sources])
const localConditions = ref([...filterStore.conditions])
const localCategories = ref([...filterStore.categories])
const localInStock = ref(filterStore.inStock !== false)

function reset() {
  localSources.value = []
  localConditions.value = []
  localCategories.value = []
  localInStock.value = true
}

function apply() {
  filterStore.sources = localSources.value
  filterStore.conditions = localConditions.value
  filterStore.categories = localCategories.value
  filterStore.inStock = localInStock.value ? true : null
  filterStore.setPage(1)
  productStore.fetchProducts()
  emit('close')
}
</script>
