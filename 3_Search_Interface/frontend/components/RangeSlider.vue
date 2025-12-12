<template>
  <div class="relative pt-6 pb-4">
    <div class="text-xs mb-3 font-medium text-gray-700">
      {{ label }}: {{ minValue.toFixed(fixedDigits) }} - {{ maxValue.toFixed(fixedDigits) }} {{ unit }}
    </div>
    
    <div 
      ref="sliderRef"
      class="relative w-full h-2 bg-gray-200 rounded-full cursor-pointer"
      @mousedown="onSliderMouseDown"
      @touchstart="onSliderTouchStart"
    >
      <div class="absolute h-full bg-gray-300 rounded-full w-full"></div>
      
      <div 
        class="absolute h-full bg-blue-500 rounded-full"
        :style="{
          left: `${selectedRange.start}%`,
          width: `${selectedRange.width}%`
        }"
      ></div>
      
      <div
        ref="minThumbRef"
        class="absolute top-1/2 transform -translate-y-1/2 w-4 h-4 bg-white border-2 border-blue-500 rounded-full shadow-md cursor-pointer z-10"
        :style="{ left: `calc(${selectedRange.start}% - 8px)` }"
        @mousedown.stop="onThumbMouseDown('min', $event)"
        @touchstart.stop="onThumbTouchStart('min', $event)"
      ></div>
      
      <div
        ref="maxThumbRef"
        class="absolute top-1/2 transform -translate-y-1/2 w-4 h-4 bg-white border-2 border-blue-500 rounded-full shadow-md cursor-pointer z-10"
        :style="{ left: `calc(${selectedRange.end}% - 8px)` }"
        @mousedown.stop="onThumbMouseDown('max', $event)"
        @touchstart.stop="onThumbTouchStart('max', $event)"
      ></div>
    </div>
    
    <div class="flex justify-between mt-1 text-xs text-gray-500">
      <span>{{ props.min }}</span>
      <span>{{ Math.round((props.max - props.min) / 2) }}</span>
      <span>{{ props.max }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

interface Props {
  modelValue: { min: number; max: number }
  min: number
  max: number
  step?: number
  label: string
  unit?: string
  fixedDigits?: number
}

const props = withDefaults(defineProps<Props>(), {
  step: 1,
  unit: '',
  fixedDigits: 0
})

const emit = defineEmits<{
  'update:modelValue': [value: { min: number; max: number }]
}>()

const sliderRef = ref<HTMLDivElement | null>(null)
const minThumbRef = ref<HTMLDivElement | null>(null)
const maxThumbRef = ref<HTMLDivElement | null>(null)

// Local values
const minValue = ref(props.modelValue.min)
const maxValue = ref(props.modelValue.max)

// Currently active thumb being dragged
const activeThumb = ref<'min' | 'max' | null>(null)

// Calculate the percentage position of the selected range
const selectedRange = computed(() => {
  const totalRange = props.max - props.min
  const startPercent = ((minValue.value - props.min) / totalRange) * 100
  const endPercent = ((maxValue.value - props.min) / totalRange) * 100
  const widthPercent = endPercent - startPercent
  
  return {
    start: Math.max(0, Math.min(startPercent, 100)),
    end: Math.max(0, Math.min(endPercent, 100)),
    width: Math.max(0, Math.min(widthPercent, 100))
  }
})

// Convert pixel position to value
const pixelToValue = (pixelX: number): number => {
  if (!sliderRef.value) return 0
  
  const rect = sliderRef.value.getBoundingClientRect()
  const percent = Math.max(0, Math.min((pixelX - rect.left) / rect.width, 1))
  const value = props.min + percent * (props.max - props.min)
  
  // Apply stepping
  return Math.round(value / props.step) * props.step
}

// Update value and ensure min <= max
const updateValue = (thumb: 'min' | 'max', value: number) => {
  const clampedValue = Math.max(props.min, Math.min(value, props.max))
  
  if (thumb === 'min') {
    minValue.value = Math.min(clampedValue, maxValue.value)
  } else {
    maxValue.value = Math.max(clampedValue, minValue.value)
  }
  
  // Ensure minimum gap (optional)
  const minGap = props.step * 2
  if (maxValue.value - minValue.value < minGap) {
    if (thumb === 'min') {
      minValue.value = maxValue.value - minGap
    } else {
      maxValue.value = minValue.value + minGap
    }
  }
  
  // Emit update event
  emit('update:modelValue', {
    min: minValue.value,
    max: maxValue.value
  })
}

// Mouse event handlers
const onThumbMouseDown = (thumb: 'min' | 'max', event: MouseEvent) => {
  event.preventDefault()
  activeThumb.value = thumb
  
  const onMouseMove = (moveEvent: MouseEvent) => {
    if (activeThumb.value) {
      updateValue(activeThumb.value, pixelToValue(moveEvent.clientX))
    }
  }
  
  const onMouseUp = () => {
    activeThumb.value = null
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }
  
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

// Touch event handlers
const onThumbTouchStart = (thumb: 'min' | 'max', event: TouchEvent) => {
  event.preventDefault()
  activeThumb.value = thumb
  
  const onTouchMove = (moveEvent: TouchEvent) => {
    if (activeThumb.value && moveEvent.touches[0]) {
      updateValue(activeThumb.value, pixelToValue(moveEvent.touches[0].clientX))
    }
  }
  
  const onTouchEnd = () => {
    activeThumb.value = null
    document.removeEventListener('touchmove', onTouchMove)
    document.removeEventListener('touchend', onTouchEnd)
  }
  
  document.addEventListener('touchmove', onTouchMove)
  document.addEventListener('touchend', onTouchEnd)
}

// Click track to directly set range
const onSliderMouseDown = (event: MouseEvent) => {
  if (event.target === sliderRef.value) {
    const value = pixelToValue(event.clientX)
    const rangeCenter = (minValue.value + maxValue.value) / 2
    
    if (value < rangeCenter) {
      // Clicked left side, adjust min value
      updateValue('min', value)
    } else {
      // Clicked right side, adjust max value
      updateValue('max', value)
    }
  }
}

const onSliderTouchStart = (event: TouchEvent) => {
  if (event.target === sliderRef.value && event.touches[0]) {
    const value = pixelToValue(event.touches[0].clientX)
    const rangeCenter = (minValue.value + maxValue.value) / 2
    
    if (value < rangeCenter) {
      updateValue('min', value)
    } else {
      updateValue('max', value)
    }
  }
}

// Watch for external value changes
const updateFromProps = () => {
  minValue.value = props.modelValue.min
  maxValue.value = props.modelValue.max
}

// Respond to external value changes
watch(() => props.modelValue, updateFromProps, { deep: true })

onMounted(updateFromProps)
</script>

<style scoped>
/* Thumb hover effect */
.min-thumb:hover, .max-thumb:hover {
  transform: scale(1.1);
  transition: transform 0.1s;
}

/* Prevent text selection */
div {
  user-select: none;
}
</style>