<template>
  <div class="min-h-screen">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRatesStore } from '@/stores/ratesStore'

const ratesStore = useRatesStore()
onMounted(() => {
  ratesStore.fetchRates()
})
</script>
