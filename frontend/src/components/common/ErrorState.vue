<template>
  <div class="flex flex-col items-center justify-center py-20 text-center px-4">
    <div class="text-4xl mb-4">⚠</div>
    <p class="text-text-secondary text-sm">{{ message }}</p>
    <button v-if="retry" @click="$emit('retry')" class="mt-4 btn-outline text-sm">
      重試
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{ message: string; retry?: boolean }>()
defineEmits(['retry'])
</script>
