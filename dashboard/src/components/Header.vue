<script setup>
import { computed } from 'vue'

const props = defineProps({
  systemStatus: {
    type: Object,
    default: null
  }
})

// Determine status indicator color and label
const statusInfo = computed(() => {
  const status = props.systemStatus?.status || 'no_data'
  
  switch (status) {
    case 'live':
      return { color: 'bg-green-500', pulse: true, label: 'LIVE' }
    case 'delayed':
      return { color: 'bg-yellow-500', pulse: true, label: 'DELAYED' }
    case 'offline':
      return { color: 'bg-red-500', pulse: false, label: 'OFFLINE' }
    default:
      return { color: 'bg-gray-500', pulse: false, label: 'NO DATA' }
  }
})
</script>

<template>
  <header class="bg-[#0f172a] px-6 py-3 flex items-center justify-between border-b border-gray-800">
    <!-- Logo -->
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center">
        <span class="text-white font-bold text-lg">🚗</span>
      </div>
      <div>
        <h1 class="text-white font-bold text-xl tracking-wide">SIAPMacet</h1>
        <p class="text-gray-500 text-xs">Sukabumi Traffic Intelligence</p>
      </div>
    </div>
    
    <!-- Live Status -->
    <div class="flex items-center gap-3">
      <!-- Status Indicator -->
      <div class="flex items-center gap-2 bg-[#1e293b] px-4 py-2 rounded-full">
        <span 
          class="w-2.5 h-2.5 rounded-full"
          :class="[statusInfo.color, statusInfo.pulse ? 'animate-pulse' : '']"
        ></span>
        <span class="text-white text-sm font-medium">{{ statusInfo.label }}</span>
      </div>
    </div>
  </header>
</template>
