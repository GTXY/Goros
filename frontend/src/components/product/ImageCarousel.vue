<template>
  <div class="space-y-3">
    <!-- Main image -->
    <div
      class="relative aspect-square bg-dark rounded-lg overflow-hidden cursor-zoom-in"
      @click="lightboxOpen = true"
    >
      <img
        v-if="current"
        :src="current"
        :alt="alt"
        class="w-full h-full object-contain p-4"
        @error="onError"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <img src="/feather-watermark.svg" class="w-24 h-36 opacity-10" alt="" />
      </div>

      <!-- Arrow nav -->
      <button
        v-if="images.length > 1"
        @click.stop="prev"
        class="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-dark/80 rounded-full flex items-center justify-center text-text-secondary hover:text-gold transition-all"
      >‹</button>
      <button
        v-if="images.length > 1"
        @click.stop="next"
        class="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-dark/80 rounded-full flex items-center justify-center text-text-secondary hover:text-gold transition-all"
      >›</button>
    </div>

    <!-- Thumbnails -->
    <div v-if="images.length > 1" class="flex gap-2 overflow-x-auto pb-1">
      <button
        v-for="(img, i) in images"
        :key="i"
        @click="activeIdx = i"
        class="flex-shrink-0 w-14 h-14 rounded overflow-hidden border-2 transition-all"
        :class="i === activeIdx ? 'border-gold' : 'border-dark-border hover:border-gold/50'"
      >
        <img :src="img" :alt="`${alt} ${i + 1}`" class="w-full h-full object-contain" @error="() => {}" />
      </button>
    </div>

    <!-- Lightbox -->
    <Teleport to="body">
      <div
        v-if="lightboxOpen"
        class="fixed inset-0 z-[100] bg-black/90 flex items-center justify-center p-4"
        @click="lightboxOpen = false"
      >
        <img
          :src="current"
          class="max-w-full max-h-full object-contain"
          @click.stop
        />
        <button
          class="absolute top-4 right-4 text-white/60 hover:text-white text-2xl"
          @click="lightboxOpen = false"
        >✕</button>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{ images: string[]; alt?: string }>()
const activeIdx = ref(0)
const lightboxOpen = ref(false)

const current = computed(() => props.images?.[activeIdx.value] ?? null)

function prev() {
  activeIdx.value = (activeIdx.value - 1 + props.images.length) % props.images.length
}
function next() {
  activeIdx.value = (activeIdx.value + 1) % props.images.length
}
function onError() {
  if (activeIdx.value < props.images.length - 1) activeIdx.value++
}
</script>
