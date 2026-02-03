<script setup>
import { ref, onMounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  roads: {
    type: Object,
    default: () => ({ features: [] })
  },
  trafficData: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['road-select'])

const mapContainer = ref(null)
let map = null
let roadLayer = null
let heatLayer = null
let roadLayers = {} // Store individual road layers by road_id

const showHeatmap = ref(false)

function getTrafficColor(speed) {
  if (speed === null || speed === undefined) return '#22c55e'
  if (speed < 20) return '#ef4444' // Red - Heavy
  if (speed < 35) return '#eab308' // Yellow - Moderate
  return '#22c55e' // Green - Smooth
}

function initMap() {
  if (!mapContainer.value || map) return
  
  // Sukabumi center coordinates
  map = L.map(mapContainer.value, {
    center: [-6.92, 106.93],
    zoom: 12,
    zoomControl: true
  })
  
  // Standard OpenStreetMap tiles (light theme)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map)
  
  updateRoads()
}

function updateRoads() {
  if (!map || !props.roads.features) return
  
  // Remove existing layer
  if (roadLayer) {
    map.removeLayer(roadLayer)
  }
  roadLayers = {}
  
  // Create traffic lookup map
  const trafficMap = {}
  for (const t of props.trafficData) {
    trafficMap[t.road_id] = t
  }
  
  // Add road layer
  roadLayer = L.geoJSON(props.roads, {
    style: (feature) => {
      const traffic = trafficMap[feature.properties.road_id]
      const speed = traffic?.speed
      
      // If heatmap on, make roads transparent
      if (showHeatmap.value) {
        return { color: '#888', weight: 2, opacity: 0.3 }
      }
      
      return {
        color: getTrafficColor(speed),
        weight: 5,
        opacity: 0.9,
        lineCap: 'round',
        lineJoin: 'round'
      }
    },
    onEachFeature: (feature, layer) => {
      const roadId = feature.properties.road_id
      roadLayers[roadId] = layer
      
      const traffic = trafficMap[roadId]
      const speed = traffic?.speed || '-'
      const freeFlow = traffic?.free_flow || '-'
      const roadName = feature.properties.road_name || roadId
      const status = speed === '-' ? 'Unknown' : 
                    speed < 20 ? 'Heavy Traffic' :
                    speed < 35 ? 'Moderate Traffic' : 'Smooth'
      
      layer.bindPopup(`
        <div style="min-width: 200px; font-family: system-ui;">
          <h3 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 600;">${roadName}</h3>
          <p style="margin: 0 0 8px 0; font-size: 11px; color: #888;">${roadId}</p>
          <div style="display: flex; justify-content: space-between; font-size: 12px; color: #666;">
            <span>Speed:</span>
            <span style="font-weight: 500; color: ${getTrafficColor(speed)}">${speed} km/h</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 12px; color: #666; margin-top: 4px;">
            <span>Free Flow:</span>
            <span>${freeFlow} km/h</span>
          </div>
          <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #eee; font-size: 11px; color: #888;">
            Status: <strong>${status}</strong>
          </div>
        </div>
      `)
      
      layer.on('click', () => {
        emit('road-select', {
          ...feature.properties,
          traffic: traffic
        })
      })
    }
  }).addTo(map)
  
  // Fit bounds if we have features
  if (props.roads.features && props.roads.features.length > 0) {
    try {
      // Don't refit on updates if user moved map
      // map.fitBounds(roadLayer.getBounds(), { padding: [50, 50] })
    } catch (e) {
      // Ignore bounds error
    }
  }
}

// Focus on a specific road by ID
function focusRoad(roadId) {
  const layer = roadLayers[roadId]
  if (layer && map) {
    const bounds = layer.getBounds()
    map.flyToBounds(bounds, { 
      padding: [100, 100],
      duration: 0.8 
    })
    layer.openPopup()
    
    // Flash effect
    layer.setStyle({ weight: 10, opacity: 1 })
    setTimeout(() => {
      layer.setStyle({ weight: 5, opacity: 0.9 })
    }, 1500)
  }
}

// Toggle Heatmap
async function toggleHeatmap() {
  showHeatmap.value = !showHeatmap.value
  
  if (showHeatmap.value) {
    // Turn ON heatmap
    try {
      if (!heatLayer) {
        // Fetch data
        const res = await fetch('/api/analytics/heatmap')
        const data = await res.json()
        if (data.points && window.L && window.L.heatLayer) {
             heatLayer = window.L.heatLayer(data.points, {
                radius: 25,
                blur: 15,
                maxZoom: 15,
                max: 1.0,
                gradient: {0.4: 'green', 0.65: 'yellow', 1: 'red'}
            }).addTo(map)
        }
      } else {
        heatLayer.addTo(map)
      }
      // Dim roads
      if (roadLayer) {
        roadLayer.eachLayer(l => l.setStyle({ color: '#888', weight: 2, opacity: 0.3 }))
      }
    } catch (e) {
      console.error("Heatmap error:", e)
      showHeatmap.value = false
    }
  } else {
    // Turn OFF heatmap
    if (heatLayer) map.removeLayer(heatLayer)
    updateRoads() // Restore road colors
  }
}

// Expose focusRoad to parent
defineExpose({ focusRoad })

watch(() => [props.roads, props.trafficData], () => {
  if (!showHeatmap.value) {
    updateRoads()
  }
}, { deep: true })

onMounted(() => {
  initMap()
})
</script>

<template>
  <div ref="mapContainer" class="absolute inset-0 z-0"></div>
  
  <!-- Heatmap Toggle Button -->
  <button 
    @click="toggleHeatmap"
    class="absolute top-24 left-4 z-[500] bg-white rounded-lg shadow-lg p-2 flex items-center gap-2 hover:bg-gray-50 transition-colors"
    :class="showHeatmap ? 'ring-2 ring-red-500 bg-red-50' : ''"
  >
    <span class="text-lg">🔥</span>
    <span class="text-xs font-semibold text-gray-700">{{ showHeatmap ? 'Hide Heatmap' : 'Show Heatmap' }}</span>
  </button>
</template>

<style>
.leaflet-popup-content-wrapper {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
}

.leaflet-popup-tip {
  background: white;
  border-bottom: none; 
}

/* Fix for dark map if needed, but we use light tiles */
.leaflet-container {
    background: #0a0f1a;
}
</style>
