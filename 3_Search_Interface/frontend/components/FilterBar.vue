<template>
  <div class="px-4 md:px-8 py-2 flex items-center gap-4 overflow-x-auto no-scrollbar text-sm text-gray-600 border-t border-gray-100">
    <div class="flex items-center space-x-6 whitespace-nowrap">
      <div class="relative" ref="categoryButtonRef">
        <button
          @click="toggleCategoryMenu"
          class="flex items-center gap-1 px-3 py-1 border border-gray-300 rounded-full hover:bg-gray-50 hover:text-black transition"
        >
          Category: {{ displayCategory }}
          <svg 
            class="w-4 h-4 transition-transform"
            :class="{ 'rotate-180': showCategoryMenu }"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </button>
        
        <Teleport to="body">
          <div 
            v-if="showCategoryMenu"
            data-category-menu
            @click.stop
            :style="categoryMenuStyle"
            class="fixed w-64 bg-white shadow-lg rounded-lg border border-gray-100 py-2 z-[100] max-h-96 overflow-y-auto"
          >
            <div
              @click="updateCategory('All')"
              class="px-4 py-2 hover:bg-gray-100 cursor-pointer font-medium"
              :class="{ 'bg-blue-50 text-blue-700': filters.category === 'All' }"
            >
              All
            </div>
            <div class="border-t border-gray-200 my-1"></div>
            
            <div
              v-for="(subCategories, mainCategory) in categoryStructure"
              :key="mainCategory"
              class="mb-1"
            >
              <div
                @click.stop="updateCategory(mainCategory)"
                class="px-4 py-2 hover:bg-gray-100 cursor-pointer font-semibold text-gray-800"
                :class="{ 'bg-blue-50 text-blue-700': filters.category === mainCategory }"
              >
                {{ mainCategory }}
              </div>
              
              <div
                v-for="subCategory in subCategories"
                :key="`${mainCategory}-${subCategory}`"
                @click.stop="updateCategory(`${mainCategory} > ${subCategory}`)"
                class="px-8 py-1.5 hover:bg-gray-100 cursor-pointer text-sm text-gray-600"
                :class="{ 'bg-blue-50 text-blue-700': filters.category === `${mainCategory} > ${subCategory}` }"
              >
                └ {{ subCategory }}
              </div>
            </div>
          </div>
        </Teleport>
      </div>

      <div class="relative" ref="companyButtonRef">
        <button
          @click="toggleCompanyMenu"
          class="flex items-center gap-1 px-3 py-1 border border-gray-300 rounded-full hover:bg-gray-50 hover:text-black transition"
        >
          Company: {{ filters.company }}
          <svg 
            class="w-4 h-4 transition-transform"
            :class="{ 'rotate-180': showCompanyMenu }"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </button>
        
        <Teleport to="body">
          <div 
            v-if="showCompanyMenu"
            data-company-menu
            @click.stop
            :style="companyMenuStyle"
            class="fixed w-48 bg-white shadow-lg rounded-lg border border-gray-100 py-2 z-[100]"
          >
            <div
              v-for="comp in companyOptions"
              :key="comp"
              @click="updateCompany(comp)"
              class="px-4 py-2 hover:bg-gray-100 cursor-pointer"
              :class="{ 'bg-blue-50 text-blue-700': filters.company === comp }"
            >
              {{ comp }}
            </div>
          </div>
        </Teleport>
      </div>

      <div class="w-40">
        <RangeSlider
          v-model="rangeFilters.salt"
          :min="0"
          :max="10"
          :step="0.1"
          label="Salt"
          unit="g"
          :fixed-digits="1"
          @update:model-value="updateRangeFilter('salt', $event)"
        />
      </div>

      <div class="w-40">
        <RangeSlider
          v-model="rangeFilters.fat"
          :min="0"
          :max="100"
          :step="1"
          label="Fat"
          unit="g"
          @update:model-value="updateRangeFilter('fat', $event)"
        />
      </div>

      <div class="w-40">
        <RangeSlider
          v-model="rangeFilters.calories"
          :min="0"
          :max="2000"
          :step="50"
          label="Calories"
          unit="cal"
          @update:model-value="updateRangeFilter('calories', $event)"
        />
      </div>

      <button @click="resetFilters" class="text-blue-600 hover:underline ml-4 text-xs">
        Clear
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, nextTick, reactive, watch } from 'vue'
import type { Filters, RangeFilters } from '../composables/useFoodData'
import RangeSlider from './RangeSlider.vue'

interface Props {
  filters: Filters
  categoryStructure: Record<string, string[]>
}

const props = defineProps<Props>()

// Update emit types to support range filters
const emit = defineEmits<{
  'update:filters': [filters: Filters]
  'update:range-filters': [rangeFilters: RangeFilters]
}>()

const companyOptions = ['All', "McDonald's", "Wendy's", 'KFC']

// Control category menu display
const showCategoryMenu = ref(false)
const categoryButtonRef = ref<HTMLElement | null>(null)
const categoryMenuStyle = ref({ top: '0px', left: '0px' })

// Control company menu display
const showCompanyMenu = ref(false)
const companyButtonRef = ref<HTMLElement | null>(null)
const companyMenuStyle = ref({ top: '0px', left: '0px' })

// Range filter state (for range slider)
const rangeFilters = reactive<RangeFilters>({
  salt: { min: 0, max: props.filters.salt },
  fat: { min: 0, max: props.filters.fat },
  calories: { min: 0, max: props.filters.calories }
})

// Watch external filters changes to update rangeFilters
watch(() => props.filters, (newFilters) => {
  rangeFilters.salt.max = newFilters.salt
  rangeFilters.fat.max = newFilters.fat
  rangeFilters.calories.max = newFilters.calories
}, { deep: true })

// Update range filter
const updateRangeFilter = (key: 'salt' | 'fat' | 'calories', value: { min: number; max: number }) => {
  const newFilters = { 
    ...props.filters, 
    [key]: value.max  // Backwards compatibility: use max value
  }
  emit('update:filters', newFilters)
  
  // Also send range filter update
  const newRangeFilters = { ...rangeFilters, [key]: value }
  emit('update:range-filters', newRangeFilters)
}

// The rest of the original code remains unchanged...
const toggleCategoryMenu = async () => {
  showCategoryMenu.value = !showCategoryMenu.value
  showCompanyMenu.value = false // Close company menu
  if (showCategoryMenu.value) {
    await nextTick()
    updateCategoryMenuPosition()
  }
}

const toggleCompanyMenu = async () => {
  showCompanyMenu.value = !showCompanyMenu.value
  showCategoryMenu.value = false // Close category menu
  if (showCompanyMenu.value) {
    await nextTick()
    updateCompanyMenuPosition()
  }
}

// Update category menu position
const updateCategoryMenuPosition = () => {
  if (!categoryButtonRef.value) return
  
  const rect = categoryButtonRef.value.getBoundingClientRect()
  categoryMenuStyle.value = {
    top: `${rect.bottom}px`,
    left: `${rect.left}px`
  }
}

// Update company menu position
const updateCompanyMenuPosition = () => {
  if (!companyButtonRef.value) return
  
  const rect = companyButtonRef.value.getBoundingClientRect()
  companyMenuStyle.value = {
    top: `${rect.bottom}px`,
    left: `${rect.left}px`
  }
}

// Close menu on click outside
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  
  // Check category menu
  if (categoryButtonRef.value && !categoryButtonRef.value.contains(target)) {
    const menu = document.querySelector('[data-category-menu]')
    if (menu && !menu.contains(target)) {
      showCategoryMenu.value = false
    }
  }
  
  // Check company menu
  if (companyButtonRef.value && !companyButtonRef.value.contains(target)) {
    const menu = document.querySelector('[data-company-menu]')
    if (menu && !menu.contains(target)) {
      showCompanyMenu.value = false
    }
  }
}

// Update menu position on window resize
const handleResize = () => {
  if (showCategoryMenu.value) {
    updateCategoryMenuPosition()
  }
  if (showCompanyMenu.value) {
    updateCompanyMenuPosition()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('resize', handleResize)
  
  // Initialize rangeFilters
  rangeFilters.salt = { min: 0, max: props.filters.salt }
  rangeFilters.fat = { min: 0, max: props.filters.fat }
  rangeFilters.calories = { min: 0, max: props.filters.calories }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('resize', handleResize)
})

// Display current selected category
const displayCategory = computed(() => {
  if (props.filters.category === 'All') return 'All'
  const parts = props.filters.category.split(' > ')
  if (parts.length === 2) {
    return `${parts[0]} > ${parts[1]}`
  }
  return props.filters.category
})

// Update category
const updateCategory = (cat: string) => {
  const newFilters = { ...props.filters, category: cat }
  emit('update:filters', newFilters)
  showCategoryMenu.value = false
}

// Update company
const updateCompany = (comp: string) => {
  const newFilters = { ...props.filters, company: comp }
  emit('update:filters', newFilters)
  showCompanyMenu.value = false
}

const resetFilters = () => {
  const newFilters = {
    category: 'All',
    company: 'All',
    salt: 10,
    fat: 100,
    calories: 2000
  }
  
  // Simultaneously reset rangeFilters
  rangeFilters.salt = { min: 0, max: 10 }
  rangeFilters.fat = { min: 0, max: 100 }
  rangeFilters.calories = { min: 0, max: 2000 }
  
  emit('update:filters', newFilters)
  emit('update:range-filters', rangeFilters)
}
</script>

<style scoped>
/* Hide scrollbar but allow scrolling */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>