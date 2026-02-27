<template>
  <div class="shap-waterfall-container">
    <ClientOnly>
      <VChart :option="chartOption" autoresize class="chart" @click="handleChartClick" />
      <template #fallback>
        <div class="flex items-center justify-center h-full">
          <div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
      </template>
    </ClientOnly>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  evidence: {
    type: Array,
    required: true,
    default: () => []
  },
  title: {
    type: String,
    default: 'Risk Factor Contributions'
  }
})

const emit = defineEmits(['askAbout'])

const handleChartClick = (params) => {
  if (params.data && params.data.evidence) {
    emit('askAbout', {
      type: 'shap',
      feature: params.data.evidence.feature,
      contribution: params.data.evidence.contribution,
      explanation: params.data.evidence.explanation,
      category: params.data.evidence.risk_category
    })
  }
}

// Format feature names for display
const formatFeatureName = (feature) => {
  if (!feature) return 'Unknown'
  return feature
    .replace(/_/g, ' ')
    .replace(/(\d+)([dhmw])/g, ' $1$2')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

// Process evidence data - deduplicate and aggregate by feature
const processedData = computed(() => {
  if (!props.evidence || props.evidence.length === 0) return []

  // Flatten all evidence from alerts
  const allEvidence = props.evidence.flatMap(alert =>
    (alert.evidence || []).map(e => ({
      ...e,
      alertId: alert.alert_id,
      signal: alert.signal
    }))
  )

  // Deduplicate by feature name - keep the one with highest absolute contribution
  const featureMap = new Map()
  allEvidence.forEach(e => {
    const feature = e.feature
    const existing = featureMap.get(feature)
    if (!existing || Math.abs(e.contribution || 0) > Math.abs(existing.contribution || 0)) {
      featureMap.set(feature, e)
    }
  })

  // Convert to array and sort by absolute contribution (descending)
  const deduplicated = Array.from(featureMap.values())
    .sort((a, b) => Math.abs(b.contribution || 0) - Math.abs(a.contribution || 0))
    .slice(0, 6) // Top 6 features

  // Reverse for bottom-to-top display (smallest at bottom, largest at top)
  return deduplicated.slice().reverse()
})

const chartOption = computed(() => {
  const data = processedData.value

  if (data.length === 0) {
    return {
      title: {
        text: 'No SHAP data available',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#94a3b8',
          fontSize: 14
        }
      }
    }
  }

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const item = params[0]
        const evidence = item.data.evidence
        const contribution = evidence.contribution || 0
        const impact = contribution > 0 ? 'INCREASED' : 'DECREASED'
        const impactColor = contribution > 0 ? '#DC2626' : '#10B981'

        return `
          <div style="min-width: 220px;">
            <div style="font-weight: 600; margin-bottom: 6px;">${formatFeatureName(evidence.feature)}</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span>Contribution:</span>
              <span style="font-weight: 600; color: ${impactColor}">
                ${contribution > 0 ? '+' : ''}${contribution.toFixed(4)}
              </span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span>Impact:</span>
              <span style="color: ${impactColor}; font-weight: 500;">${impact} risk</span>
            </div>
            ${evidence.explanation ? `
            <div style="border-top: 1px solid #e5e7eb; margin-top: 8px; padding-top: 8px; font-size: 11px; color: #64748b;">
              ${evidence.explanation}
            </div>
            ` : ''}
            <div style="margin-top: 8px; font-size: 10px; color: #94a3b8; text-align: center;">
              Click to ask AI SENTINEL
            </div>
          </div>
        `
      },
      backgroundColor: 'white',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      textStyle: {
        color: '#1e293b'
      },
      extraCssText: 'box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);'
    },
    grid: {
      left: '3%',
      right: '12%',
      bottom: '3%',
      top: '8%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#e5e7eb'
        }
      },
      axisLabel: {
        color: '#64748b',
        fontSize: 10,
        formatter: (value) => value.toFixed(2)
      },
      splitLine: {
        lineStyle: {
          color: '#f1f5f9',
          type: 'dashed'
        }
      }
    },
    yAxis: {
      type: 'category',
      data: data.map(d => formatFeatureName(d.feature)),
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#475569',
        fontSize: 11,
        width: 120,
        overflow: 'truncate'
      }
    },
    series: [
      {
        name: 'Contribution',
        type: 'bar',
        data: data.map(d => {
          const val = d.contribution || 0
          const isPositive = val > 0
          return {
            value: val,
            evidence: d,
            itemStyle: {
              color: isPositive ? '#DC2626' : '#10B981',
              borderRadius: isPositive ? [0, 4, 4, 0] : [4, 0, 0, 4]
            },
            label: {
              show: true,
              position: 'right',
              formatter: isPositive ? `+${val.toFixed(3)}` : val.toFixed(3),
              color: isPositive ? '#DC2626' : '#10B981',
              fontSize: 10,
              fontWeight: 'bold',
              distance: 5
            }
          }
        }),
        barWidth: '50%',
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.15)'
          }
        }
      }
    ],
    animation: true,
    animationDuration: 600,
    animationEasing: 'cubicOut'
  }
})
</script>

<style scoped>
.shap-waterfall-container {
  position: relative;
  width: 100%;
  height: 260px;
}

.chart {
  width: 100%;
  height: 100%;
  cursor: pointer;
}
</style>
