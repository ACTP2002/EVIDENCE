<template>
  <div class="risk-doughnut-container">
    <div class="chart-wrapper">
      <ClientOnly>
        <VChart :option="chartOption" autoresize class="chart" @click="handleChartClick" />
        <template #fallback>
          <div class="flex items-center justify-center h-full">
            <div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>
        </template>
      </ClientOnly>
      <!-- Center score display -->
      <div class="center-score">
        <div class="score-value" :class="scoreColorClass">{{ totalScore }}</div>
        <div class="score-label">RISK SCORE</div>
      </div>
    </div>
    <!-- Legend below chart -->
    <div class="legend-container">
      <div
        v-for="item in props.data"
        :key="item.category"
        class="legend-item"
        @click="handleLegendClick(item)"
      >
        <span class="legend-dot" :style="{ backgroundColor: getColor(item.category) }"></span>
        <span class="legend-label">{{ item.category }}</span>
        <span class="legend-value">{{ item.score }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  maxScore: {
    type: Number,
    default: 100
  },
  caseScore: {
    type: Number,
    default: null  // When provided, use backend score; otherwise compute from data
  }
})

const emit = defineEmits(['askAbout'])

const handleChartClick = (params) => {
  if (params.data && params.data.name !== 'Remaining') {
    emit('askAbout', {
      type: 'risk',
      category: params.data.name,
      score: params.data.value
    })
  }
}

const handleLegendClick = (item) => {
  emit('askAbout', {
    type: 'risk',
    category: item.category,
    score: item.score
  })
}

// Risk colors matching Tailwind config
const riskColors = {
  'Liquidity Shift': '#DC2626',
  'Multi-Accounting': '#EA580C',
  'Monetary Deviation': '#F59E0B',
  'Geographic': '#F97316',
  'Behavioral': '#EAB308',
  'Authentication Anomaly': '#7C3AED',
  'Impossible Travel': '#DB2777',
  'Account Takeover': '#BE123C',
  'Velocity Anomaly': '#EA580C',
  'Money Laundering': '#991B1B',
  'Structuring': '#B91C1C',
  'Market Manipulation': '#9333EA',
  'Collusion': '#7C3AED',
  'Other': '#6B7280'
}

const getColor = (category) => {
  if (riskColors[category]) return riskColors[category]
  const lowerCat = category.toLowerCase()
  if (lowerCat.includes('liquidity')) return '#DC2626'
  if (lowerCat.includes('multi') || lowerCat.includes('accounting')) return '#EA580C'
  if (lowerCat.includes('monetary') || lowerCat.includes('deviation')) return '#F59E0B'
  if (lowerCat.includes('geographic') || lowerCat.includes('geo')) return '#F97316'
  if (lowerCat.includes('behav')) return '#EAB308'
  if (lowerCat.includes('auth') || lowerCat.includes('login')) return '#7C3AED'
  if (lowerCat.includes('travel') || lowerCat.includes('impossible')) return '#DB2777'
  if (lowerCat.includes('takeover')) return '#BE123C'
  if (lowerCat.includes('velocity')) return '#EA580C'
  if (lowerCat.includes('launder') || lowerCat.includes('aml')) return '#991B1B'
  if (lowerCat.includes('structur')) return '#B91C1C'
  if (lowerCat.includes('manipulat') || lowerCat.includes('market')) return '#9333EA'
  if (lowerCat.includes('collusion') || lowerCat.includes('coordinat')) return '#7C3AED'
  return '#6B7280'
}

// Computed sum from breakdown categories (for chart proportions)
const computedSum = computed(() => {
  return props.data.reduce((sum, item) => sum + (item.score || 0), 0)
})

// Display score: use backend caseScore if provided, otherwise use computed sum
const totalScore = computed(() => {
  return props.caseScore !== null ? props.caseScore : computedSum.value
})

// Remaining gap based on the display score
const remaining = computed(() => {
  return Math.max(0, props.maxScore - totalScore.value)
})

const scoreColorClass = computed(() => {
  if (totalScore.value >= 80) return 'text-risk-critical'
  if (totalScore.value >= 60) return 'text-risk-high'
  if (totalScore.value >= 40) return 'text-risk-medium'
  return 'text-risk-low'
})

const chartOption = computed(() => {
  // Scale factor to match backend score visually
  // If caseScore=89 but computed sum=84, scale categories up so ring proportions are correct
  const scaleFactor = (props.caseScore !== null && computedSum.value > 0)
    ? totalScore.value / computedSum.value
    : 1

  // Build data array with remaining gap
  const chartData = props.data.map(item => ({
    value: item.score * scaleFactor,  // Scale for visual proportion
    name: item.category,
    itemStyle: {
      color: getColor(item.category)
    }
  }))

  // Add remaining segment if not at 100%
  if (remaining.value > 0) {
    chartData.push({
      value: remaining.value,
      name: 'Remaining',
      itemStyle: {
        color: '#f1f5f9' // slate-100 - very light gray
      },
      emphasis: {
        disabled: true
      }
    })
  }

  return {
    tooltip: {
      show: false // Disable tooltip, we have legend below
    },
    series: [
      {
        name: 'Risk Breakdown',
        type: 'pie',
        radius: ['60%', '85%'],
        center: ['50%', '50%'],
        startAngle: 90,
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        labelLine: {
          show: false
        },
        emphasis: {
          scale: false,
          itemStyle: {
            shadowBlur: 0
          }
        },
        data: chartData
      }
    ],
    animation: true,
    animationDuration: 800,
    animationEasing: 'cubicOut'
  }
})
</script>

<style scoped>
.risk-doughnut-container {
  width: 100%;
}

.chart-wrapper {
  position: relative;
  width: 100%;
  height: 140px;
}

.chart {
  width: 100%;
  height: 100%;
}

.center-score {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}

.score-value {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 0.625rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 2px;
}

.legend-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.15s;
}

.legend-item:hover {
  background-color: #f8fafc;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  font-size: 0.75rem;
  color: #475569;
}

.legend-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: #1e293b;
}
</style>
