<script setup>
defineProps({
  progress: {
    type: Number,
    default: 0
  },
  statusText: {
    type: String,
    default: 'Loading...'
  }
})
</script>

<template>
  <div class="fixed inset-0 bg-[#0a0f1a] z-50 flex flex-col items-center justify-center">
    <!-- Logo -->
    <div class="mb-8">
      <div class="w-16 h-16 rounded-full bg-blue-500/20 flex items-center justify-center mb-4 mx-auto">
        <svg class="w-8 h-8 text-blue-500 animate-spin" viewBox="0 0 24 24" fill="none">
          <path d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12" 
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
    </div>
    
    <!-- Title -->
    <h1 class="text-3xl font-bold text-white mb-2">Initializing SIAPMacet Protocol...</h1>
    <p class="text-gray-400 mb-8">Connecting to Sukabumi Traffic Grid</p>
    
    <!-- Progress Bar -->
    <div class="w-96 mb-4">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
      </div>
    </div>
    
    <!-- Status -->
    <div class="flex items-center justify-between w-96 text-sm">
      <span class="text-gray-500">{{ statusText }}</span>
      <span class="text-gray-400 font-medium">{{ progress }}%</span>
    </div>
    
    <!-- Preview Cards -->
    <div class="flex gap-4 mt-12">
      <!-- Map Legend Card -->
      <div class="glass-card p-4 w-56">
        <div class="flex items-center justify-between mb-4">
          <span class="text-sm font-medium text-gray-300">MAP LEGEND</span>
          <svg class="w-6 h-6 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 6a3 3 0 013-3h10a1 1 0 01.8 1.6L14.25 8l2.55 3.4A1 1 0 0116 13H6a1 1 0 00-1 1v3a1 1 0 11-2 0V6z"/>
          </svg>
        </div>
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-red-500"></span>
              <span class="text-sm text-gray-400">0-20 km/h</span>
            </div>
            <span class="badge badge-heavy">HEAVY</span>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-yellow-500"></span>
              <span class="text-sm text-gray-400">20-40 km/h</span>
            </div>
            <span class="badge badge-moderate">MODERATE</span>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-green-500"></span>
              <span class="text-sm text-gray-400">&gt;40 km/h</span>
            </div>
            <span class="badge badge-smooth">SMOOTH</span>
          </div>
        </div>
      </div>
      
      <!-- Live Monitor Card -->
      <div class="glass-card p-4 w-56">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-medium text-red-400">LIVE MONITOR</span>
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-white">Jl. Ahmad Yani</h3>
        <p class="text-xs text-gray-500 mb-3">Cisaat - Cibadak Corridor</p>
        <div class="flex items-baseline gap-1 mb-4">
          <span class="text-4xl font-bold text-white">--</span>
          <span class="text-sm text-gray-400">km/h</span>
        </div>
        <div class="flex gap-1 mb-2">
          <div class="h-6 w-8 bg-blue-900/50 rounded"></div>
          <div class="h-6 w-8 bg-blue-800/50 rounded"></div>
          <div class="h-6 w-8 bg-blue-700/50 rounded"></div>
          <div class="h-6 w-8 bg-blue-600/50 rounded"></div>
          <div class="h-6 w-8 bg-blue-500/50 rounded"></div>
          <div class="h-6 w-8 bg-red-500/50 rounded"></div>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-yellow-500"></span>
          <span class="text-xs text-yellow-500">Loading data...</span>
        </div>
      </div>
      
      <!-- Stats Card -->
      <div class="glass-card p-4 w-56">
        <div class="space-y-4">
          <!-- Weather Alert 1 -->
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-gray-700/50 flex items-center justify-center">
              <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M5.5 16a3.5 3.5 0 01-.369-6.98 4 4 0 117.753-1.977A4.5 4.5 0 1113.5 16h-8z"/>
              </svg>
            </div>
            <div class="flex-1">
              <div class="text-sm font-medium text-white">14:00 PM</div>
              <div class="text-xs text-gray-500">Heavy rain expected in CBD</div>
            </div>
            <span class="badge badge-high">HIGH IMPACT</span>
          </div>
          
          <!-- Weather Alert 2 -->
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-gray-700/50 flex items-center justify-center">
              <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M5.5 16a3.5 3.5 0 01-.369-6.98 4 4 0 117.753-1.977A4.5 4.5 0 1113.5 16h-8z"/>
              </svg>
            </div>
            <div class="flex-1">
              <div class="text-sm font-medium text-white">16:00 PM</div>
              <div class="text-xs text-gray-500">Overcast, reduced visibility</div>
            </div>
            <span class="badge badge-med">MED IMPACT</span>
          </div>
          
          <!-- Stats Row -->
          <div class="flex gap-3 pt-2">
            <div class="flex-1 bg-gray-800/50 rounded-lg p-3 text-center">
              <div class="text-xs text-gray-500 mb-1">ACTIVE CAMS</div>
              <div class="text-2xl font-bold text-white">--</div>
              <div class="flex items-center justify-center gap-1 mt-1">
                <span class="w-2 h-2 rounded-full bg-green-500"></span>
                <span class="text-xs text-green-500">Online</span>
              </div>
            </div>
            <div class="flex-1 bg-gray-800/50 rounded-lg p-3 text-center">
              <div class="text-xs text-gray-500 mb-1">REPORTS</div>
              <div class="text-2xl font-bold text-white">--</div>
              <div class="flex items-center justify-center gap-1 mt-1">
                <span class="text-xs text-yellow-500">⚠ New</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Footer -->
    <div class="absolute bottom-6 text-xs text-gray-600">
      v2.4.0-alpha • Sukabumi Smart City Initiative
    </div>
  </div>
</template>
