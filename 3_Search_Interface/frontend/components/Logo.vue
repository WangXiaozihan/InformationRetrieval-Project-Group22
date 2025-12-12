<template>
  <h1 
    :class="sizeClass" 
    class="font-bold cursor-pointer select-none"
    @click="handleClick"
  >
    <span class="text-blue-500">F</span>
    <span class="text-red-500">o</span>
    <span class="text-yellow-500">o</span>
    <span class="text-blue-500">d</span>
    <span class="text-green-500">l</span>
    <span class="text-red-500">e</span>
  </h1>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'small' | 'large'
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'small',
  clickable: true
})

const emit = defineEmits<{
  click: []
}>()

const sizeClass = computed(() => {
  return props.size === 'large' ? 'text-8xl' : 'text-4xl'
})

const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

