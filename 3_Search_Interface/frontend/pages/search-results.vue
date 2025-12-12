<template>
  <div class="min-h-screen flex flex-col bg-white">
    <div class="flex flex-col h-full">
      <div class="sticky top-0 bg-white z-50 shadow-sm border-b border-gray-200">
        <div class="flex items-center p-4 md:px-8 py-4 gap-4 md:gap-8">
          <Logo @click="goHome" />

          <div class="flex-grow max-w-2xl relative">
            <SearchBar
              v-model="localSearchQuery"
              @search="performSearch"
              @clear="handleClearSearch"
            />
          </div>
        </div>

        <FilterBar 
          :filters="filters" 
          :category-structure="categoryStructure" 
          @update:filters="handleFilterUpdate"
          @update:range-filters="handleRangeFilterUpdate"
        />
      </div>

      <div class="flex-grow bg-gray-50 px-4 md:px-8 py-6">
        <div class="max-w-6xl mx-auto">
          <p v-if="hasSearched" class="text-gray-500 text-sm mb-6">
            {{ displayedResults.length }} results ({{ searchTime }} seconds)
          </p>

          <div v-if="!hasSearched" class="flex flex-col items-center justify-center py-20 text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <p class="text-lg mb-2">Enter a search term to find products</p>
            <p class="text-sm">Try searching for "burger", "fries", or "chicken"</p>
          </div>

          <div v-else-if="isLoading" class="flex justify-center py-10">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>

          <div
            v-else-if="displayedResults.length > 0"
            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
          >
            <ProductCard
              v-for="item in displayedResults"
              :key="item.product_id"
              :product="item"
            />
          </div>

          <div
            v-else-if="hasSearched && displayedResults.length === 0"
            class="flex flex-col items-center justify-center py-20 text-gray-500"
          >
            <p class="text-lg mb-2">No results found for "{{ searchQuery }}"</p>
            <p class="text-sm">Try adjusting the filters or using different keywords</p>
            <button
              @click="resetFilters"
              class="mt-4 text-blue-600 hover:underline"
            >
              Reset all filters
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'nuxt/app'
import type { Filters } from '../composables/useFoodData'
import { useHead } from 'nuxt/app'
import { useFoodData } from '../composables/useFoodData'

const route = useRoute()
const router = useRouter()

// Page metadata
useHead({
  title: 'Search Results - Foodle',
  meta: [
    { name: 'description', content: 'Search results for food nutrition information' }
  ]
})

// Search query - Initialize from URL parameter
const searchQuery = ref(route.query.q as string || '')
// Local search term - Used for input box, does not automatically trigger search
const localSearchQuery = ref(route.query.q as string || '')

// Has search been performed
const hasSearched = ref(false)

// Search time
const searchTime = ref(0)

// Filter state
const filters = reactive<Filters>({
  category: 'All',
  company: 'All',
  salt: 10,
  fat: 100,
  calories: 2000
})

// Range filter state (for front-end filtering)
const rangeFilters = reactive({
  salt: { min: 0, max: 10 },
  fat: { min: 0, max: 100 },
  calories: { min: 0, max: 2000 }
})

// Use composable
const { allFoodItems, categoryStructure, filterFoods, fetchFoodData, isLoading } = useFoodData()

// Handle clearing search - Just clear the input box
const handleClearSearch = () => {
  localSearchQuery.value = ''
}

// Safe sessionStorage operation functions
const getFromSessionStorage = (key: string, defaultValue: any): string => {
  if (import.meta.client && typeof sessionStorage !== 'undefined') {
    return sessionStorage.getItem(key) || defaultValue
  }
  return defaultValue
}

const setToSessionStorage = (key: string, value: string) => {
  if (import.meta.client && typeof sessionStorage !== 'undefined') {
    sessionStorage.setItem(key, value)
  }
}

const removeFromSessionStorage = (key: string) => {
  if (import.meta.client && typeof sessionStorage !== 'undefined') {
    sessionStorage.removeItem(key)
  }
}

// Save filter state to sessionStorage
const saveFiltersToStorage = () => {
  setToSessionStorage('searchFilters_category', filters.category)
  setToSessionStorage('searchFilters_company', filters.company)
  setToSessionStorage('searchFilters_salt_min', rangeFilters.salt.min.toString())
  setToSessionStorage('searchFilters_salt_max', rangeFilters.salt.max.toString())
  setToSessionStorage('searchFilters_fat_min', rangeFilters.fat.min.toString())
  setToSessionStorage('searchFilters_fat_max', rangeFilters.fat.max.toString())
  setToSessionStorage('searchFilters_calories_min', rangeFilters.calories.min.toString())
  setToSessionStorage('searchFilters_calories_max', rangeFilters.calories.max.toString())
}

// Initialize filters from URL parameters and sessionStorage
const initializeFilters = () => {
  if (import.meta.client) {
    Object.assign(filters, {
      category: (route.query.category as string) || getFromSessionStorage('searchFilters_category', 'All'),
      company: (route.query.company as string) || getFromSessionStorage('searchFilters_company', 'All'),
      salt: Number(route.query.salt) || Number(getFromSessionStorage('searchFilters_salt_max', 10)),
      fat: Number(route.query.fat) || Number(getFromSessionStorage('searchFilters_fat_max', 100)),
      calories: Number(route.query.calories) || Number(getFromSessionStorage('searchFilters_calories_max', 2000))
    })
    
    // Initialize range filters
    Object.assign(rangeFilters, {
      salt: {
        min: Number(getFromSessionStorage('searchFilters_salt_min', 0)),
        max: filters.salt
      },
      fat: {
        min: Number(getFromSessionStorage('searchFilters_fat_min', 0)),
        max: filters.fat
      },
      calories: {
        min: Number(getFromSessionStorage('searchFilters_calories_min', 0)),
        max: filters.calories
      }
    })
  }
}

// Perform search
const performSearch = async () => {
  const query = localSearchQuery.value.trim()
  if (query !== '') {
    // Update actual search query
    searchQuery.value = query
    hasSearched.value = true
    
    // Save filter state
    saveFiltersToStorage()
    
    // Update URL parameters, including filters
    const queryParams: any = { q: query }
    
    // Only add filters to URL if they are not default values
    if (filters.category !== 'All') queryParams.category = filters.category
    if (filters.company !== 'All') queryParams.company = filters.company
    if (filters.salt !== 10) queryParams.salt = filters.salt
    if (filters.fat !== 100) queryParams.fat = filters.fat
    if (filters.calories !== 2000) queryParams.calories = filters.calories
    
    router.replace({
      query: queryParams
    })
    
    const startTime = Date.now()
    try {
      await fetchFoodData(query, filters)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      searchTime.value = Number(((Date.now() - startTime) / 1000).toFixed(2))
    }
  }
}

// Handle filter update
const handleFilterUpdate = async (newFilters: Filters) => {
  Object.assign(filters, newFilters)
  
  // Synchronize update of max values for range filters
  rangeFilters.salt.max = newFilters.salt
  rangeFilters.fat.max = newFilters.fat
  rangeFilters.calories.max = newFilters.calories
  
  // Save filter state
  saveFiltersToStorage()
  
  if (hasSearched.value) {
    const startTime = Date.now()
    try {
      await fetchFoodData(searchQuery.value, filters)
      
      // Update URL parameters
      const queryParams: any = { q: searchQuery.value }
      
      // Only add filters to URL if they are not default values
      if (filters.category !== 'All') queryParams.category = filters.category
      if (filters.company !== 'All') queryParams.company = filters.company
      if (filters.salt !== 10) queryParams.salt = filters.salt
      if (filters.fat !== 100) queryParams.fat = filters.fat
      if (filters.calories !== 2000) queryParams.calories = filters.calories
      
      router.replace({
        query: queryParams
      })
    } catch (error) {
      console.error('Filter update failed:', error)
    } finally {
      searchTime.value = Number(((Date.now() - startTime) / 1000).toFixed(2))
    }
  }
}

// Handle range filter update (Front-end filtering)
const handleRangeFilterUpdate = (newRangeFilters: any) => {
  Object.assign(rangeFilters, newRangeFilters)
  
  // Update max value of main filters (for backward compatibility)
  filters.salt = newRangeFilters.salt.max
  filters.fat = newRangeFilters.fat.max
  filters.calories = newRangeFilters.calories.max
  
  // Save filter state
  saveFiltersToStorage()
  
  // If a search has been performed, no need to re-call API, front-end filtering is enough
  console.log('Range filters updated:', newRangeFilters)
}

// Final displayed results - Apply front-end filtering
const displayedResults = computed(() => {
  if (!hasSearched.value) return []
  
  return allFoodItems.value.filter(item => {
    // Numerical range filtering
    const matchesSalt = (item.salt || 0) >= rangeFilters.salt.min && 
                       (item.salt || 0) <= rangeFilters.salt.max
    
    const matchesFat = (item.fat || 0) >= rangeFilters.fat.min && 
                      (item.fat || 0) <= rangeFilters.fat.max
    
    const matchesCalories = (item.calories || 0) >= rangeFilters.calories.min && 
                           (item.calories || 0) <= rangeFilters.calories.max
    
    // Category filtering
    let matchesCategory = true
    if (filters.category && filters.category !== 'All') {
      if (filters.category.includes(' > ')) {
        const [filterMain, filterSub] = filters.category.split(' > ')
        const itemParts = item.category.split(' > ')
        const itemMain = itemParts[0]
        const itemSub = itemParts[1] || ''
        matchesCategory = itemMain === filterMain && itemSub === filterSub
      } else {
        const itemMain = item.category.split(' > ')[0]
        matchesCategory = itemMain === filters.category
      }
    }
    
    // Company filtering
    const matchesCompany = !filters.company || filters.company === 'All' || 
      item.company === filters.company
    
    return matchesSalt && matchesFat && matchesCalories && matchesCategory && matchesCompany
  })
})

// Go to home page
const goHome = () => {
  router.push('/')
}

// Reset all filters
const resetFilters = () => {
  filters.category = 'All'
  filters.company = 'All'
  filters.salt = 10
  filters.fat = 100
  filters.calories = 2000
  
  // Reset range filters
  rangeFilters.salt = { min: 0, max: 10 }
  rangeFilters.fat = { min: 0, max: 100 }
  rangeFilters.calories = { min: 0, max: 2000 }
  
  // Clear stored filter state
  removeFromSessionStorage('searchFilters_category')
  removeFromSessionStorage('searchFilters_company')
  removeFromSessionStorage('searchFilters_salt_min')
  removeFromSessionStorage('searchFilters_salt_max')
  removeFromSessionStorage('searchFilters_fat_min')
  removeFromSessionStorage('searchFilters_fat_max')
  removeFromSessionStorage('searchFilters_calories_min')
  removeFromSessionStorage('searchFilters_calories_max')
  
  // If a search has been performed, re-search
  if (hasSearched.value) {
    handleFilterUpdate(filters)
  }
}

// Watch route changes to handle returning from product details page
watch(() => route.query, (newQuery) => {
  // If returning from product details page (has fromSearch flag), restore filter state
  if (newQuery.fromSearch === 'true') {
    // Restore filter state from sessionStorage
    const savedCategory = getFromSessionStorage('searchFilters_category', 'All')
    const savedCompany = getFromSessionStorage('searchFilters_company', 'All')
    const savedSaltMin = getFromSessionStorage('searchFilters_salt_min', '0')
    const savedSaltMax = getFromSessionStorage('searchFilters_salt_max', '10')
    const savedFatMin = getFromSessionStorage('searchFilters_fat_min', '0')
    const savedFatMax = getFromSessionStorage('searchFilters_fat_max', '100')
    const savedCaloriesMin = getFromSessionStorage('searchFilters_calories_min', '0')
    const savedCaloriesMax = getFromSessionStorage('searchFilters_calories_max', '2000')
    
    if (savedCategory) filters.category = savedCategory
    if (savedCompany) filters.company = savedCompany
    
    // Restore range filters
    rangeFilters.salt = {
      min: Number(savedSaltMin),
      max: Number(savedSaltMax)
    }
    rangeFilters.fat = {
      min: Number(savedFatMin),
      max: Number(savedFatMax)
    }
    rangeFilters.calories = {
      min: Number(savedCaloriesMin),
      max: Number(savedCaloriesMax)
    }
    
    // Update main filters
    filters.salt = rangeFilters.salt.max
    filters.fat = rangeFilters.fat.max
    filters.calories = rangeFilters.calories.max
    
    const { fromSearch, ...cleanQuery } = newQuery
    router.replace({ query: cleanQuery })
  }
})

// Initialize filters and search when the page loads
onMounted(() => {
  initializeFilters()
  
  if (searchQuery.value) {
    performSearch()
  }
})
</script>