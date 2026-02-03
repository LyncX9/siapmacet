<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import LoadingScreen from './components/LoadingScreen.vue'
import Header from './components/Header.vue'
import MapView from './components/MapView.vue'
import Sidebar from './components/Sidebar.vue'
import TrafficLegend from './components/TrafficLegend.vue'

const isLoading = ref(true)
const loadingProgress = ref(0)
const loadingText = ref('Connecting to Sukabumi Traffic Grid...')

const roads = ref({ features: [] })
const trafficData = ref([])
const forecastData = ref(null)
const systemStatus = ref(null)
const selectedRoad = ref(null)
const mapRef = ref(null)

let refreshInterval = null
let statusInterval = null

const API_BASE = '/api'

async function loadData() {
  try {
    // Fetch roads
    loadingText.value = 'Fetching road geometry...'
    loadingProgress.value = 30
    const roadsRes = await fetch(`${API_BASE}/roads`)
    roads.value = await roadsRes.json()
    
    // Fetch traffic
    loadingText.value = 'Loading traffic data...'
    loadingProgress.value = 60
    const trafficRes = await fetch(`${API_BASE}/traffic_snapshot`)
    trafficData.value = await trafficRes.json()
    
    // Fetch system status
    await fetchSystemStatus()
    
    // Fetch forecast (phased)
    loadingText.value = 'Initializing forecast engine...'
    loadingProgress.value = 85
    try {
      const forecastRes = await fetch(`${API_BASE}/forecast`)
      const data = await forecastRes.json()
      if (!data.error) {
        forecastData.value = data
      }
    } catch (e) {
      console.log('Forecast not available yet')
    }
    
    loadingText.value = 'System ready!'
    loadingProgress.value = 100
    
    // Delay to show completion
    await new Promise(r => setTimeout(r, 800))
    isLoading.value = false
    
  } catch (error) {
    console.error('Error loading data:', error)
    loadingText.value = 'Connection error. Retrying...'
    setTimeout(loadData, 3000)
  }
}

async function fetchSystemStatus() {
  try {
    const res = await fetch(`${API_BASE}/system_status`)
    systemStatus.value = await res.json()
  } catch (e) {
    systemStatus.value = { status: 'offline', status_label: 'Offline' }
  }
}

function handleRoadSelect(road) {
  selectedRoad.value = road
}

// Focus map on a specific road
function focusOnRoad(roadId) {
  // Focus map
  if (mapRef.value) {
    mapRef.value.focusRoad(roadId)
  }
  
  // Set selected road for analytics
  if (roads.value?.features) {
    const feature = roads.value.features.find(f => f.properties.road_id === roadId)
    if (feature) {
      selectedRoad.value = feature
    }
  }
}

// Auto refresh traffic data every 60 seconds
function startAutoRefresh() {
  refreshInterval = setInterval(async () => {
    try {
      const trafficRes = await fetch(`${API_BASE}/traffic_snapshot`)
      trafficData.value = await trafficRes.json()
      
      const forecastRes = await fetch(`${API_BASE}/forecast`)
      const data = await forecastRes.json()
      if (!data.error) {
        forecastData.value = data
      }
    } catch (e) {
      console.log('Refresh failed')
    }
  }, 60000)
  
  // Update status more frequently (every 10 seconds)
  statusInterval = setInterval(fetchSystemStatus, 10000)
}

onMounted(() => {
  loadData()
  startAutoRefresh()
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
  if (statusInterval) clearInterval(statusInterval)
})
</script>

<template>
  <!-- Loading Screen -->
  <LoadingScreen 
    v-if="isLoading" 
    :progress="loadingProgress"
    :statusText="loadingText"
  />
  
  <!-- Main Dashboard -->
  <div v-else class="h-screen w-screen flex flex-col bg-[#0a0f1a]">
    <!-- Header -->
    <Header :systemStatus="systemStatus" />
    
    <!-- Main Content -->
    <div class="flex-1 relative overflow-hidden">
      <!-- Map (Background) -->
      <MapView 
        ref="mapRef"
        :roads="roads" 
        :trafficData="trafficData"
        @road-select="handleRoadSelect"
      />
      
      <!-- Traffic Legend (Bottom Left) -->
      <TrafficLegend class="absolute bottom-6 left-6 z-[1000]" />
      
      <!-- Sidebar (Right) -->
      <Sidebar 
        :roads="roads"
        :trafficData="trafficData"
        :forecastData="forecastData"
        :systemStatus="systemStatus"
        :selectedRoad="selectedRoad"
        @focus-road="focusOnRoad"
        class="absolute top-4 right-4 z-[1000]"
      />
    </div>
    
    <!-- Footer -->
    <div class="py-2 text-center text-xs text-gray-500">
      v2.4.0-alpha • Sukabumi Smart City Initiative
    </div>
  </div>
</template>
