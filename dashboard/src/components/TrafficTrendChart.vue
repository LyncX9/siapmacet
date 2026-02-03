<script setup>
import { computed, onMounted } from 'vue'
import { Chart } from 'chart.js/auto'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  roadName: {
    type: String,
    default: 'Road Traffic'
  }
})

let chartInstance = null

onMounted(() => {
  renderChart()
})

// Watch for data changes to update chart
import { watch } from 'vue'
watch(() => props.data, () => {
  renderChart()
}, { deep: true })

function renderChart() {
  const ctx = document.getElementById('trendChart')
  if (!ctx || !props.data.length) return

  if (chartInstance) {
    chartInstance.destroy()
  }

  const labels = props.data.map(d => d.time_label)
  const speeds = props.data.map(d => d.avg_speed)

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Avg Speed (km/h)',
        data: speeds,
        borderColor: '#60a5fa', // Blue-400
        backgroundColor: 'rgba(96, 165, 250, 0.1)',
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointRadius: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          mode: 'index',
          intersect: false,
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            color: '#9ca3af'
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            color: '#9ca3af',
            maxTicksLimit: 6
          }
        }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      }
    }
  })
}
</script>

<template>
  <div class="w-full h-48 bg-white/5 rounded-lg p-2">
    <div v-if="!data.length" class="h-full flex items-center justify-center text-gray-400 text-xs">
      No historical data available
    </div>
    <canvas v-else id="trendChart"></canvas>
  </div>
</template>
