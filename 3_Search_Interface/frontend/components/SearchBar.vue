<template>
  <div class="flex-grow max-w-2xl relative">
    <div
      :class="[
        'flex items-center border border-gray-200 rounded-full px-4 py-2 shadow-sm hover:shadow-md bg-white transition-shadow',
        isLarge ? 'px-5 py-3' : ''
      ]"
    >
      <span class="text-gray-400 mr-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </span>
      <input
        v-model="localQuery"
        type="text"
        :class="[
          'flex-grow outline-none text-gray-700 bg-transparent',
          isLarge ? 'text-lg' : 'text-base'
        ]"
        :placeholder="placeholder"
        @keyup.enter="handleSearch"
        ref="inputRef"
      />
      
      <button
        v-if="localQuery"
        @click="clearSearch"
        class="text-gray-400 hover:text-gray-600 p-1 mr-2 transition"
        title="Clear search"
        type="button"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      
      <button
        @click="handleSearch"
        :class="[
          'text-blue-500 font-bold cursor-pointer hover:text-blue-700 transition',
          !isLarge ? 'border-l pl-3 border-gray-300' : 'px-3'
        ]"
        title="Search"
        type="button"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'

interface Props {
  modelValue: string
  isLarge?: boolean
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  isLarge: false,
  placeholder: 'Search for burgers, fries...'
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'search': []
  'clear': []
}>()

const inputRef = ref<HTMLInputElement | null>(null)

const localQuery = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const handleSearch = () => {
  emit('search')
}

const clearSearch = () => {
  localQuery.value = ''
  emit('clear')
  // Focus on the input field after clearing
  nextTick(() => {
    inputRef.value?.focus()
  })
}
</script>