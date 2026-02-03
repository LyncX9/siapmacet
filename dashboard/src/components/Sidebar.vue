<script setup>
import { computed, ref, watch } from 'vue'
import TrafficTrendChart from './TrafficTrendChart.vue'

const props = defineProps({
  roads: {
    type: Object,
    default: () => ({ features: [] })
  },
  trafficData: {
    type: Array,
    default: () => []
  },
  forecastData: {
    type: Object,
    default: null
  },
  systemStatus: {
    type: Object,
    default: null
  },
  selectedRoad: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['focus-road'])

// Format seconds ago to human readable
const lastUpdated = computed(() => {
  const seconds = props.systemStatus?.seconds_ago
  
  if (seconds === null || seconds === undefined) {
    return 'NO DATA'
  }
  
  if (seconds < 60) {
    return `${seconds}S AGO`
  } else if (seconds < 3600) {
    return `${Math.floor(seconds / 60)}M AGO`
  } else if (seconds < 86400) {
    return `${Math.floor(seconds / 3600)}H AGO`
  } else {
    return `${Math.floor(seconds / 86400)}D AGO`
  }
})

// Computed stats
const avgSpeed = computed(() => {
  if (!props.trafficData.length) return 0
  const sum = props.trafficData.reduce((acc, t) => acc + (t.speed || 0), 0)
  return Math.round(sum / props.trafficData.length)
})

const congestionLevel = computed(() => {
  if (avgSpeed.value >= 35) return { label: 'Low', color: 'text-green-400' }
  if (avgSpeed.value >= 20) return { label: 'Medium', color: 'text-yellow-400' }
  return { label: 'High', color: 'text-red-400' }
})

const heavyCount = computed(() => {
  return props.trafficData.filter(t => t.speed && t.speed < 20).length
})

const moderateCount = computed(() => {
  return props.trafficData.filter(t => t.speed && t.speed >= 20 && t.speed < 35).length
})

const smoothCount = computed(() => {
  return props.trafficData.length - heavyCount.value - moderateCount.value
})

// Helper to get road name from road_id
function getRoadName(roadId) {
  if (props.roads.features) {
    const feature = props.roads.features.find(f => f.properties.road_id === roadId)
    if (feature) {
      return feature.properties.road_name || roadId
    }
  }
  return roadId
}

// ALL congested roads - DEDUPLICATED by road_id
const congestedRoads = computed(() => {
  const roadMap = new Map()
  
  props.trafficData.forEach(t => {
    if (t.speed && t.speed < 35) {
      const existing = roadMap.get(t.road_id)
      if (!existing || t.speed < existing.speed) {
        roadMap.set(t.road_id, {
          ...t,
          road_name: getRoadName(t.road_id),
          status: t.speed < 20 ? 'heavy' : 'moderate'
        })
      }
    }
  })
  
  return Array.from(roadMap.values()).sort((a, b) => (a.speed || 0) - (b.speed || 0))
})

// Forecast data from API
const forecast = computed(() => props.forecastData || null)
const isMLReady = computed(() => forecast.value?.data_status?.is_ml_ready || false)
const dataProgress = computed(() => forecast.value?.data_status?.data_collection_progress || 0)
const daysRemaining = computed(() => forecast.value?.data_status?.days_remaining || 30)
const overallConfidence = computed(() => forecast.value?.overall_confidence || 0)

// Analytics Data
const trendData = ref([])
const isFetchingTrend = ref(false)

// Fetch trend data when selected road changes
watch(() => props.selectedRoad, async (road) => {
  if (road) {
    isFetchingTrend.value = true
    try {
      const res = await fetch(`/api/analytics/hourly/${road.properties.road_id}`)
      trendData.value = await res.json()
    } catch (e) {
      console.error('Failed to load trend data', e)
      trendData.value = []
    } finally {
      isFetchingTrend.value = false
    }
  } else {
    trendData.value = []
  }
})

// Handle road click
function handleRoadClick(roadId) {
  emit('focus-road', roadId)
}
</script>

<template>
  <div class="w-80 bg-[#1e3a5f] rounded-xl p-4 shadow-2xl max-h-[calc(100vh-100px)] overflow-y-auto">
    
    <!-- Live Snapshot -->
    <div class="mb-4">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-blue-400"></div>
          <span class="text-sm font-semibold text-white">Live Snapshot</span>
        </div>
        <span class="text-xs text-gray-400">UPDATED {{ lastUpdated }}</span>
      </div>
      
      <div class="grid grid-cols-2 gap-3">
        <div class="bg-white/10 rounded-lg p-3">
          <div class="text-xs text-gray-300 mb-1">Avg Speed</div>
          <div class="text-3xl font-bold text-white">{{ avgSpeed }}<span class="text-sm text-gray-300 ml-1">km/h</span></div>
        </div>
        <div class="bg-white/10 rounded-lg p-3">
          <div class="text-xs text-gray-300 mb-1">Congestion</div>
          <div class="text-2xl font-bold" :class="congestionLevel.color">{{ congestionLevel.label }}</div>
        </div>
      </div>
    </div>
    
    <!-- Selected Road Analytics (shows when road is selected) -->
    <div v-if="selectedRoad" class="mb-4 animate-in fade-in slide-in-from-right-4 duration-300">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-sm font-semibold text-white truncate max-w-[200px]">{{ selectedRoad.properties.road_name }}</h3>
        <span class="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded">Selected</span>
      </div>
      
      <div class="bg-[#0f172a]/50 rounded-lg p-3 border border-white/5">
         <h4 class="text-xs text-gray-400 mb-2">24h Speed Trend</h4>
         <div v-if="isFetchingTrend" class="h-48 flex items-center justify-center">
            <span class="text-xs text-blue-400 animate-pulse">Loading analytics...</span>
         </div>
         <TrafficTrendChart v-else :data="trendData" />
      </div>
    </div>
    
    <!-- Divider -->
    <div class="border-t border-white/10 my-4"></div>
    
    <!-- Traffic Forecast -->
    <div class="mb-4">
      <div class="flex items-center justify-between mb-2">
        <div>
          <h3 class="text-sm font-semibold text-white">Traffic Forecast</h3>
          <p class="text-xs text-gray-400">Next 60 minutes</p>
        </div>
        <div class="text-right">
          <div class="flex items-center gap-1">
            <span class="text-xs text-gray-400">Confidence:</span>
            <span 
              class="text-xs font-bold"
              :class="overallConfidence >= 70 ? 'text-green-400' : overallConfidence >= 40 ? 'text-yellow-400' : 'text-orange-400'"
            >
              {{ overallConfidence }}%
            </span>
          </div>
          <div class="text-[10px] text-gray-500">
            {{ isMLReady ? 'ML Active' : 'Estimation' }}
          </div>
        </div>
      </div>
      
      <!-- Bar Chart with Confidence -->
      <div v-if="forecast?.forecasts" class="mb-3">
        <div class="flex items-end justify-between h-20 px-1">
          <div class="flex flex-col items-center gap-1 flex-1">
            <div class="w-10 rounded-t bg-blue-600" :style="{ height: '40px' }"></div>
            <span class="text-[10px] text-gray-400">NOW</span>
          </div>
          <div v-for="(fc, i) in forecast.forecasts" :key="fc.time_label" class="flex flex-col items-center gap-1 flex-1">
            <div class="relative">
              <div 
                class="w-10 rounded-t"
                :class="fc.congestion_level === 'heavy' ? 'bg-red-500' : fc.congestion_level === 'moderate' ? 'bg-yellow-500' : 'bg-blue-500'"
                :style="{ height: `${20 + (fc.avg_speed / 60) * 40}px`, opacity: fc.confidence / 100 }"
              ></div>
              <span class="absolute -top-4 left-1/2 -translate-x-1/2 text-[8px] text-gray-400">{{ fc.confidence }}%</span>
            </div>
            <span class="text-[10px] text-gray-400">{{ fc.time_label }}</span>
          </div>
        </div>
      </div>
      
      <!-- Data Collection Status (if ML not ready) -->
      <div v-if="!isMLReady" class="bg-orange-500/10 border border-orange-400/30 rounded-lg p-3 mt-2">
        <div class="flex items-start gap-2">
          <span class="text-orange-400 mt-0.5">📊</span>
          <div class="flex-1">
            <h4 class="text-xs font-medium text-orange-300">Data Collection Mode</h4>
            <p class="text-[11px] text-gray-300 mt-1">
              ML Prediction akan aktif setelah 30 hari data terkumpul.
            </p>
            <div class="mt-2">
              <div class="flex justify-between text-[10px] text-gray-400 mb-1">
                <span>Progress</span>
                <span>{{ Math.round(dataProgress) }}%</span>
              </div>
              <div class="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-gradient-to-r from-orange-500 to-yellow-400 rounded-full transition-all"
                  :style="{ width: `${dataProgress}%` }"
                ></div>
              </div>
              <div class="text-[10px] text-gray-500 mt-1">
                ~{{ daysRemaining }} hari lagi
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- ML Ready Badge -->
      <div v-else class="bg-green-500/10 border border-green-400/30 rounded-lg p-2 mt-2 flex items-center gap-2">
        <span class="text-green-400">✓</span>
        <span class="text-xs text-green-300">ML Prediction Active</span>
      </div>
    </div>
    
    <!-- Divider -->
    <div class="border-t border-white/10 my-4"></div>
    
    <!-- Expect Delays -->
    <div class="mb-4">
      <div class="flex items-center gap-2 mb-3">
        <span class="text-blue-400">⚠️</span>
        <h3 class="text-sm font-semibold text-white">Expect Delays</h3>
        <span class="text-xs bg-red-500/30 text-red-300 px-2 py-0.5 rounded-full">
          {{ congestedRoads.length }}
        </span>
      </div>
      
      <div v-if="congestedRoads.length > 0" class="space-y-2 max-h-32 overflow-y-auto">
        <div 
          v-for="road in congestedRoads" 
          :key="road.road_id"
          class="bg-white/5 rounded-lg p-2 flex items-center justify-between hover:bg-white/10 transition-colors cursor-pointer"
          @click="handleRoadClick(road.road_id)"
        >
          <div class="flex-1 min-w-0">
            <div class="text-sm text-white font-medium truncate">{{ road.road_name }}</div>
            <div class="text-xs text-gray-400">{{ road.speed }} km/h</div>
          </div>
          <span 
            class="text-xs px-2 py-1 rounded ml-2 flex-shrink-0"
            :class="road.status === 'heavy' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'"
          >
            {{ road.status === 'heavy' ? 'Heavy' : 'Moderate' }}
          </span>
        </div>
      </div>
      
      <div v-else class="text-center py-3 bg-green-500/10 rounded-lg">
        <span class="text-green-400 text-sm">✓ All roads smooth</span>
      </div>
    </div>
    
    <!-- Divider -->
    <div class="border-t border-white/10 my-4"></div>
    
    <!-- Road Statistics -->
    <div>
      <h3 class="text-sm font-semibold text-white mb-3">Road Statistics</h3>
      
      <div class="grid grid-cols-3 gap-2">
        <div class="bg-red-500/20 rounded-lg p-2 text-center">
          <div class="text-xl font-bold text-red-400">{{ heavyCount }}</div>
          <div class="text-[10px] text-gray-300">Heavy</div>
        </div>
        <div class="bg-yellow-500/20 rounded-lg p-2 text-center">
          <div class="text-xl font-bold text-yellow-400">{{ moderateCount }}</div>
          <div class="text-[10px] text-gray-300">Moderate</div>
        </div>
        <div class="bg-green-500/20 rounded-lg p-2 text-center">
          <div class="text-xl font-bold text-green-400">{{ smoothCount }}</div>
          <div class="text-[10px] text-gray-300">Smooth</div>
        </div>
      </div>
    </div>
    
  </div>
</template>
