<template>
  <div class="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-lg transition-shadow overflow-hidden flex flex-col relative">
    <div class="absolute top-2 right-2 z-10 flex flex-col items-center gap-1">
      <button
        @click.stop="toggleLike"
        class="p-1 rounded-full bg-white bg-opacity-80 hover:bg-opacity-100 transition hover:text-green-500"
        :class="{
          'text-green-500': hasLiked,
          'text-gray-400': !hasLiked
        }"
        :disabled="isLiking || hasLiked"
      >
        <svg 
          class="w-5 h-5" 
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z"/>
        </svg>
      </button>
      
      <span class="text-xs text-gray-700 font-medium">{{ product.likes || 0 }}</span>
      
      <button
        @click.stop="toggleDislike"
        class="p-1 rounded-full bg-white bg-opacity-80 hover:bg-opacity-100 transition hover:text-red-500"
        :class="{
          'text-red-500': hasDisliked,
          'text-gray-400': !hasDisliked
        }"
        :disabled="isDisliking || hasDisliked"
      >
        <svg 
          class="w-5 h-5" 
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path d="M18 9.5a1.5 1.5 0 11-3 0v-6a1.5 1.5 0 013 0v6zM14 9.667v-5.43a2 2 0 00-1.106-1.79l-.05-.025A4 4 0 0011.057 2H5.64a2 2 0 00-1.962 1.608l-1.2 6A2 2 0 004.44 12H8v4a2 2 0 002 2 1 1 0 001-1v-.667a4 4 0 01.8-2.4l1.4-1.866a4 4 0 00.8-2.4z"/>
        </svg>
      </button>
      
      <span class="text-xs text-gray-700 font-medium">{{ product.dislikes || 0 }}</span>
    </div>

    <NuxtLink
      :to="getProductLink"
      class="flex flex-col flex-grow"
    >
      <div class="h-40 w-full bg-gray-100 relative flex items-center justify-center overflow-hidden">
        <img
          :src="product.image_url || `https://placehold.co/400x300?text=${encodeURIComponent(product.name)}`"
          :alt="product.name"
          class="object-cover w-full h-full opacity-90 hover:opacity-100 transition"
          @error="handleImageError"
        />
        <span
          class="absolute top-2 left-2 text-xs font-bold px-2 py-1 rounded text-white shadow-sm"
          :class="{
            'bg-yellow-500': product.company === 'McDonald\'s',
            'bg-red-600': product.company === 'Wendy\'s',
            'bg-red-500': product.company === 'KFC'
          }"
        >
          {{ product.company }}
        </span>
        <span
          v-if="product.flag"
          class="absolute bottom-2 left-2 text-xs font-bold px-2 py-1 rounded bg-red-500 text-white shadow-sm"
        >
          {{ product.flag }}
        </span>
      </div>

      <div class="p-4 flex flex-col flex-grow">
        <div class="text-xs text-gray-500 mb-1">{{ product.category }}</div>
        <h3 class="text-lg font-medium text-blue-700 mb-2 hover:underline cursor-pointer truncate">
          {{ product.name }}
        </h3>

        <p class="text-sm text-gray-600 line-clamp-2 mb-4">{{ displayDescription }}</p>

        <div
          class="mt-auto pt-3 border-t border-gray-100 grid grid-cols-3 gap-2 text-center text-xs text-gray-500"
        >
          <div>
            <div class="font-semibold text-gray-700">{{ product.calories || 'N/A' }}</div>
            <div>Cal</div>
          </div>
          <div>
            <div class="font-semibold text-gray-700">{{ product.fat || 'N/A' }}g</div>
            <div>Fat</div>
          </div>
          <div>
            <div class="font-semibold text-gray-700">{{ product.salt || 'N/A' }}g</div>
            <div>Salt</div>
          </div>
        </div>
      </div>
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'nuxt/app'
import type { NormalizedFoodItem } from '../composables/useFoodData'

interface Props {
  product: NormalizedFoodItem
}

const props = defineProps<Props>()
const route = useRoute()
// Assuming useFoodData is defined elsewhere, no translation needed for function names
const { likeProduct, dislikeProduct } = useFoodData()

const isLiking = ref(false)
const isDisliking = ref(false)

// Use local state to record user's action
const hasLiked = ref(false)
const hasDisliked = ref(false)

// Get product link, including source information
const getProductLink = computed(() => {
  // Check if current page is search results page
  const isFromSearchResults = route.path === '/search-results'
  
  if (isFromSearchResults) {
    // If navigating from search results, add a flag
    return {
      path: `/product/${props.product.product_id}`,
      query: { 
        fromSearch: 'true',
        // Keep search query for returning
        q: route.query.q || ''
      }
    }
  } else {
    // Direct navigation otherwise
    return `/product/${props.product.product_id}`
  }
})

// Toggle like status - only allows one like
const toggleLike = async () => {
  if (isLiking.value || hasLiked.value || hasDisliked.value) return // If already liked or disliked, prevent click
  
  try {
    isLiking.value = true
    
    // Set local state to liked
    hasLiked.value = true
    
    // Send like request
    await likeProduct(props.product.product_id)
    
  } catch (error) {
    console.error('Failed to like product:', error)
    // Rollback local state if failed
    hasLiked.value = false
  } finally {
    isLiking.value = false
  }
}

// Toggle dislike status - only allows one dislike
const toggleDislike = async () => {
  if (isDisliking.value || hasDisliked.value || hasLiked.value) return // If already disliked or liked, prevent click
  
  try {
    isDisliking.value = true
    
    // Set local state to disliked
    hasDisliked.value = true
    
    // Send dislike request
    await dislikeProduct(props.product.product_id)
    
  } catch (error) {
    console.error('Failed to dislike product:', error)
    // Rollback local state if failed
    hasDisliked.value = false
  } finally {
    isDisliking.value = false
  }
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = `https://placehold.co/400x300?text=${encodeURIComponent(img.alt)}`
}

// Handle description
const displayDescription = computed(() => {
  const desc = props.product.description;
  
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
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>