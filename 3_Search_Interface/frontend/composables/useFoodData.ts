
import { computed, ref, readonly } from 'vue'
import { useState } from 'nuxt/app'
import { getCategoryStructure, getCategoryMapping } from './useCategoryMapping'

// Food data interface definition (based on backend data structure)
export interface FoodItem {
  id: number;
  url: string;
  product_name: string;
  brand: string;
  original_category: string;
  category_main: string;
  category_sub: string;
  description: string;
  image_url: string;
  components_list: string[];
  ingredients_text: string;
  calories_kcal: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
  sugar_g: number;
  salt_g: number;
  likes: number;      // Added
  dislikes: number;   // Added
}

export interface NormalizedFoodItem {
  product_id: string;
  name: string;
  company: string;
  category: string;
  description: string;
  image_url: string;
  calories: number;
  fat: number;
  salt: number;
  protein: number;
  carbs: number;
  sugar: number;
  likes: number;      // Added
  dislikes: number;   // Added
  flag?: string;
  nutrition: {
    summary: Record<string, any>;
  };
  allergens_ingredients: {
    ingredients: string[];
    allergens_contains: string[];
    allergens_may_contain: string[];
    allergy_advice: string;
    preparation_notes: string;
  };
  url: string;
  ingredients_text: string;
  components_list: string[];
}

export interface Filters {
  category: string;
  company: string;
  salt: number;
  fat: number;
  calories: number;
}

// Add range filter interface
export interface RangeFilters {
  salt: { min: number; max: number }
  fat: { min: number; max: number }
  calories: { min: number; max: number }
}

// Normalize food data - Convert from Solr data structure
function normalizeFoodItem(item: any): NormalizedFoodItem {
  // Helper function: Safely extract array or single value
  const extractValue = (value: any): any => {
    if (Array.isArray(value)) {
      return value[0] || value || 0;
    }
    return value || 0;
  };

  // Helper function to concatenate category if both parts exist
  const getFullCategory = (main: any, sub: any): string => {
    const mainCat = main || 'Other';
    const subCat = sub || '';
    return subCat ? `${mainCat} > ${subCat}` : mainCat;
  };

  return {
    product_id: item.id?.toString() || Math.random().toString(),
    name: item.product_name || 'Unknown Product',
    company: item.brand || 'Unknown Brand',
    category: getFullCategory(item.category_main, item.category_sub),
    description: item.description || 'No description available',
    image_url: item.image_url || `https://placehold.co/400x300?text=Food+Item`,
    calories: extractValue(item.calories_kcal),
    fat: extractValue(item.fat_g),
    salt: extractValue(item.salt_g),
    protein: extractValue(item.protein_g),
    carbs: extractValue(item.carbs_g),
    sugar: extractValue(item.sugar_g),
    // Changed to likes and dislikes
    likes: extractValue(item.likes),
    dislikes: extractValue(item.dislikes),
    ingredients_text: item.ingredients_text || '',
    components_list: Array.isArray(item.components_list) ? item.components_list : [],
    nutrition: {
      summary: {
        calories: extractValue(item.calories_kcal),
        protein: extractValue(item.protein_g),
        fat: extractValue(item.fat_g),
        carbohydrates: extractValue(item.carbs_g),
        sugar: extractValue(item.sugar_g),
        salt: extractValue(item.salt_g)
      }
    },
    allergens_ingredients: {
      ingredients: Array.isArray(item.components_list) ? item.components_list : [],
      allergens_contains: [],
      allergens_may_contain: [],
      allergy_advice: '',
      preparation_notes: ''
    },
    url: item.url || '#'
  }
}

// ... Previous code remains unchanged ...

export const useFoodData = () => {
  // Use useState to cache the processed data
  const foodItemsCache = useState<NormalizedFoodItem[]>('food-items', () => [])
  // Loading status
  const isLoading = useState<boolean>('food-loading', () => false)
  // Save the current search state
  const currentSearchQuery = useState<string>('current-search-query', () => '')
  const currentFilters = useState<Filters>('current-filters', () => ({
    category: 'All',
    company: 'All',
    salt: 10,
    fat: 100,
    calories: 2000
  }))

  // Function to fetch data from Solr
  const fetchFoodData = async (searchQuery: string = '', filters: Filters = {} as Filters): Promise<NormalizedFoodItem[]> => {
    try {
      isLoading.value = true
      
      // Save the current search state
      if (searchQuery !== undefined) {
        currentSearchQuery.value = searchQuery
      }
      if (Object.keys(filters).length > 0) {
        currentFilters.value = { ...currentFilters.value, ...filters }
      }
      
      const params = new URLSearchParams({
        q: currentSearchQuery.value || '*:*',
        wt: 'json',
        rows: '500'
      })

      // Use saved filters
      if (currentFilters.value.calories) {
        params.append('fq', `calories_kcal:[0 TO ${currentFilters.value.calories}]`)
      }
      if (currentFilters.value.fat) {
        params.append('fq', `fat_g:[0 TO ${currentFilters.value.fat}]`)
      }
      if (currentFilters.value.salt) {
        params.append('fq', `salt_g:[0 TO ${currentFilters.value.salt}]`)
      }
      // Add company filter condition
      if (currentFilters.value.company && currentFilters.value.company !== 'All') {
        params.append('fq', `brand:"${currentFilters.value.company}"`)
      }
      
      // Add category filter condition
      if (currentFilters.value.category && currentFilters.value.category !== 'All') {
        if (currentFilters.value.category.includes(' > ')) {
          // Format: 'Main Category > Subcategory'
          const [mainCat, subCat] = currentFilters.value.category.split(' > ')
          params.append('fq', `category_main:"${mainCat}" AND category_sub:"${subCat}"`)
        } else {
          // Format: 'Main Category'
          params.append('fq', `category_main:"${currentFilters.value.category}"`)
        }
      }

      console.log('Solr Request Parameters:', params.toString())

      const response = await fetch(`/solr/solr/fastfood_menu/fastfood_search?${params}`)
      
      if (!response.ok) {
        throw new Error(`Solr request failed: ${response.status}`)
      }

      const data = await response.json()
      console.log('Solr Response Data:', data)
      
      const solrItems = data.response?.docs || []
      const normalizedData = solrItems.map((item: any) => normalizeFoodItem(item))
      
      foodItemsCache.value = normalizedData
      return normalizedData

    } catch (error) {
      console.error('Search error:', error)
      foodItemsCache.value = []
      return []
    } finally {
      isLoading.value = false
    }
  }

  // Like product - Removed unlike function
  const likeProduct = async (productId: string) => {
    try {
      // Send like request to backend
      const response = await fetch('/api/like', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          productId: productId
        })
      })

      if (!response.ok) {
        throw new Error('Like request failed')
      }

      const result = await response.json()
      
      if (result.success) {
        // Re-fetch data using the saved search state
        await fetchFoodData(currentSearchQuery.value, currentFilters.value)
        return { success: true }
      } else {
        throw new Error('Like action failed')
      }

    } catch (error) {
      console.error('Error liking product:', error)
      throw error
    }
  }

  // Dislike product - Removed undislike function
  const dislikeProduct = async (productId: string) => {
    try {
      // Send dislike request to backend
      const response = await fetch('/api/dislike', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          productId: productId
        })
      })

      if (!response.ok) {
        throw new Error('Dislike request failed')
      }

      const result = await response.json()
      
      if (result.success) {
        // Re-fetch data using the saved search state
        await fetchFoodData(currentSearchQuery.value, currentFilters.value)
        return { success: true }
      } else {
        throw new Error('Dislike action failed')
      }

    } catch (error) {
      console.error('Error disliking product:', error)
      throw error
    }
  }

  // Check if product is liked - Simplified logic
  const isProductLiked = (productId: string) => {
    // No state management needed here anymore, return false
    return false
  }

  // Check if product is disliked - Simplified logic
  const isProductDisliked = (productId: string) => {
    // No state management needed here anymore, return false
    return false
  }

  // Load all food data
  const allFoodItems = computed(() => foodItemsCache.value)

  // Get all brands
  const brands = computed(() => {
    const brandSet = new Set<string>()
    allFoodItems.value.forEach(item => {
      if (item.company) {
        brandSet.add(item.company)
      }
    })
    return Array.from(brandSet).sort()
  })

  // Get all unique categories
  const categories = computed(() => {
    const cats = new Set<string>()
    allFoodItems.value.forEach(item => {
      if (item.category) {
        cats.add(item.category)
      }
    })
    return Array.from(cats).sort()
  })

  // Get category structure (Main Category -> Subcategory)
  const categoryStructure = computed(() => {
    return getCategoryStructure()
  })

  // Get single food item by ID
  const getFoodById = (id: string): NormalizedFoodItem | undefined => {
    return allFoodItems.value.find(item => item.product_id === id)
  }

  // Filter food data
  const filterFoods = (
    items: NormalizedFoodItem[],
    searchQuery: string,
    filters: Filters
  ): NormalizedFoodItem[] => {
    const query = searchQuery.toLowerCase().trim()

    return items.filter(item => {
      // Text search
      const matchesSearch = !query || 
        item.name.toLowerCase().includes(query) ||
        item.description.toLowerCase().includes(query) ||
        item.category.toLowerCase().includes(query) ||
        (item.company && item.company.toLowerCase().includes(query))

      // Company filter
      const matchesCompany = !filters.company || filters.company === 'All' || 
        item.company === filters.company

      // Category filter
      let matchesCategory = true
      if (filters.category && filters.category !== 'All') {
        if (filters.category.includes(' > ')) {
          // Format: 'Main Category > Subcategory'
          const [filterMain, filterSub] = filters.category.split(' > ')
          const itemParts = item.category.split(' > ')
          const itemMain = itemParts[0]
          const itemSub = itemParts[1] || ''
          matchesCategory = itemMain === filterMain && itemSub === filterSub
        } else {
          // Format: 'Main Category'
          const itemMain = item.category.split(' > ')[0]
          matchesCategory = itemMain === filters.category
        }
      }

      // Numerical filters
      const matchesSalt = !filters.salt || (item.salt !== undefined && item.salt !== null && item.salt <= filters.salt)
      const matchesFat = !filters.fat || (item.fat !== undefined && item.fat !== null && item.fat <= filters.fat)
      const matchesCalories = !filters.calories || (item.calories !== undefined && item.calories !== null && item.calories <= filters.calories)

      return matchesSearch && matchesCompany && matchesCategory && 
             matchesSalt && matchesFat && matchesCalories
    })
  }

  return {
    allFoodItems,
    brands,
    categories,
    categoryStructure,
    getFoodById,
    filterFoods,
    fetchFoodData,
    likeProduct,
    dislikeProduct,
    isProductLiked,
    isProductDisliked,
    isLoading: readonly(isLoading)
  }
}