<template>
  <div class="min-h-screen bg-gray-50">
    <div class="sticky top-0 bg-white z-50 shadow-sm border-b border-gray-200">
      <div class="flex items-center p-4 md:px-8 py-4 gap-4 md:gap-8">
        <Logo @click="goHome" />
        <div class="flex-grow"></div>
        <button
          @click="goBackToSearch"
          class="text-blue-600 hover:underline text-sm"
        >
          ← Back to Search
        </button>
      </div>
    </div>

    <div v-if="product" class="max-w-6xl mx-auto px-4 md:px-8 py-8">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div class="md:flex">
          <div class="md:w-1/2 h-64 md:h-96 bg-gray-100 relative overflow-hidden">
            <img
              :src="product.image_url || `https://placehold.co/800x600?text=${encodeURIComponent(product.name)}`"
              :alt="product.name"
              class="w-full h-full object-cover"
              @error="handleImageError"
            />
            <span
              v-if="product.flag"
              class="absolute top-4 left-4 text-sm font-bold px-3 py-1 rounded bg-red-500 text-white shadow-lg"
            >
              {{ product.flag }}
            </span>
          </div>

          <div class="md:w-1/2 p-6 md:p-8">
            <div class="text-sm text-gray-500 mb-2">{{ product.category }}</div>
            <h1 class="text-3xl font-bold text-gray-800 mb-4">{{ product.name }}</h1>
            <p class="text-gray-600 mb-6 leading-relaxed">{{ displayDescription }}</p>

            <div class="mb-6">
              <span
                class="inline-block text-sm font-bold px-3 py-1 rounded text-white"
                :class="{
                  'bg-yellow-500': product.company === 'McDonald\'s',
                  'bg-red-600': product.company === 'Wendy\'s',
                  'bg-red-500': product.company === 'KFC'
                }"
              >
                {{ product.company }}
              </span>
            </div>

            <div class="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg mb-6">
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-800">{{ product.calories || 'N/A' }}</div>
                <div class="text-sm text-gray-600 mt-1">Calories</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-800">{{ product.fat || 'N/A' }}g</div>
                <div class="text-sm text-gray-600 mt-1">Fat</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-800">{{ product.salt || 'N/A' }}g</div>
                <div class="text-sm text-gray-600 mt-1">Salt</div>
              </div>
            </div>
          </div>
        </div>

        <div class="border-t border-gray-200 p-6 md:p-8">
          <div class="mb-8">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Complete Nutrition Information</h2>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Nutrient
                    </th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount per serving
                    </th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Unit
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr>
                    <td class="px-4 py-3 text-sm font-medium text-gray-700">Calories</td>
                    <td class="px-4 py-3 text-sm text-gray-900">{{ product.calories || 'N/A' }}</td>
                    <td class="px-4 py-3 text-sm text-gray-500">kcal</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-3 text-sm font-medium text-gray-700">Protein</td>
                    <td class="px-4 py-3 text-sm text-gray-900">{{ product.protein || 'N/A' }}</td>
                    <td class="px-4 py-3 text-sm text-gray-500">g</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-3 text-sm font-medium text-gray-700">Fat</td>
                    <td class="px-4 py-3 text-sm text-gray-900">{{ product.fat || 'N/A' }}</td>
                    <td class="px-4 py-3 text-sm text-gray-500">g</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-3 text-sm font-medium text-gray-700">Carbohydrates</td>
                    <td class="px-4 py-3 text-sm text-gray-900">{{ product.carbs || 'N/A' }}</td>
                    <td class="px-4 py-3 text-sm text-gray-500">g</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-3 text-sm font-medium text-gray-700">Sugar</td>
                    <td class="px-4 py-3 text-sm text-gray-900">{{ product.sugar || 'N/A' }}</td>
                    <td class="px-4 py-3 text-sm text-gray-500">g</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-3 text-sm font-medium text-gray-700">Salt</td>
                    <td class="px-4 py-3 text-sm text-gray-900">{{ product.salt || 'N/A' }}</td>
                    <td class="px-4 py-3 text-sm text-gray-500">g</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-if="product.ingredients_text && product.ingredients_text.length > 0" class="mb-8">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Ingredients</h2>
            <div class="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div class="text-gray-600 whitespace-pre-line" v-html="formatText(product.ingredients_text)"></div>
            </div>
          </div>

          <div v-if="product.url" class="mt-6">
            <a
              :href="product.url"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium"
            >
              View on {{ product.company }} Website
              <svg class="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="max-w-6xl mx-auto px-4 md:px-8 py-20">
      <div class="text-center">
        <h1 class="text-3xl font-bold text-gray-800 mb-4">Product Not Found</h1>
        <p class="text-gray-600 mb-6">The product you're looking for doesn't exist.</p>
        <button
          @click="goBackToSearch"
          class="text-blue-600 hover:underline text-sm"
        >
          ← Back to Search
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'nuxt/app'
import { useFoodData } from '../../composables/useFoodData'
import { useHead } from 'nuxt/app'

const route = useRoute()
const router = useRouter()

// Get product ID
const productId = route.params.id as string

// Use composable to fetch product data
const { getFoodById } = useFoodData()
const product = computed(() => getFoodById(productId))

// Handle description
const displayDescription = computed(() => {
  if (!product.value) return 'No product information available';
  
  const desc = product.value.description;
  
  // If it is string "{}", "[]", or empty value
  if (typeof desc === 'string') {
    const trimmed = desc.trim();
    if (trimmed === '{}' || trimmed === '[]' || trimmed === '' || trimmed === 'null') {
      return 'No description available';
    }
    return desc;
  }
  
  // If it is other types (object, array, etc.)
  if (!desc) return 'No description available';
  
  // If it is an empty object or array
  if (typeof desc === 'object' && Object.keys(desc).length === 0) {
    return 'No description available';
  }
  
  return String(desc);
});

// Page metadata
useHead({
  title: product.value ? `${product.value.name} - Foodle` : 'Product Not Found - Foodle',
  meta: [
    {
      name: 'description',
      // Use the processed description to avoid showing "{}"
      content: product.value 
        ? `Nutrition information for ${product.value.name} from ${product.value.company}. ${displayDescription.value}`
        : 'Product details page'
    }
  ]
})

// Simple text formatting function
const formatText = (text: string) => {
  if (!text) return ''
  // Only needs basic newline handling
  return text
    .replace(/\n/g, '<br>')
    .replace(/<br\s*\/?>/g, '<br>')
}

// Image error handling
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = `https://placehold.co/800x600?text=${encodeURIComponent(img.alt)}`
}

// Go to home page
const goHome = () => {
  router.push('/')
}

// Go back to search results page - Add flag to indicate return from product details
const goBackToSearch = () => {
  // Check if there is a search source flag
  const fromSearch = route.query.fromSearch === 'true'
  const searchQuery = route.query.q as string || ''
  
  if (fromSearch && searchQuery) {
    // Return to search results page and add flag
    router.push({
      path: '/search-results',
      query: { 
        q: searchQuery,
        fromSearch: 'true' // Add flag to indicate return from product details page
      }
    })
  } else {
    // If no search history, use browser back
    router.back()
  }
}

// Check if search state needs to be saved when component is mounted
onMounted(() => {
  // If navigated from search results page, ensure filter state is preserved
  if (route.query.fromSearch === 'true') {
    // No additional operation needed here, as the search results page already saved the state
    console.log('Navigated from search results, filter state should be preserved')
  }
})
</script>