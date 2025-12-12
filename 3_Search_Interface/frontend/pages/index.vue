<template>
  <div class="min-h-screen flex flex-col bg-white">
    <div class="flex flex-col items-center justify-center h-screen px-4 transition-all duration-500">
      <Logo size="large" :clickable="false" />

      <div class="w-full max-w-lg relative mt-8">
        <div class="flex items-center border border-gray-200 rounded-full px-5 py-3 shadow-sm hover:shadow-md bg-white">
          <span class="text-gray-400 mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </span>
          <input
            v-model="searchQuery"
            type="text"
            class="flex-grow outline-none text-gray-700 text-lg"
            placeholder="Search for burgers, fries..."
            @keyup.enter="goToSearchResults"
          />
          <button
            @click="goToSearchResults"
            class="ml-3 text-blue-500 font-bold cursor-pointer px-4 py-1 rounded-full hover:bg-blue-50 transition"
          >
            Search
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'nuxt/app'
import { useHead } from 'nuxt/app'

// Page metadata
useHead({
  title: 'Foodle - Nutrition Explorer',
  meta: [
    { name: 'description', content: 'Search and explore food nutrition information' }
  ]
})

const router = useRouter()
const searchQuery = ref('')

// Navigate to search results page
const goToSearchResults = () => {
  if (searchQuery.value.trim() !== '') {
    router.push({
      path: '/search-results',
      query: { q: searchQuery.value.trim() }
    })
  }
}
</script>