<template>
  <div
    ref="containerRef"
    class="network-graph-container"
    :class="{ 'fullscreen': isFullscreen }"
  >
    <ClientOnly>
      <VChart
        ref="chartRef"
        :option="chartOption"
        autoresize
        class="chart"
        @click="handleChartClick"
        @graphroam="handleGraphRoam"
      />
      <template #fallback>
        <div class="flex items-center justify-center h-full bg-slate-900 rounded-lg">
          <div class="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </template>
    </ClientOnly>

    <!-- Control Buttons -->
    <div class="controls">
      <button @click="zoomIn" class="control-btn" title="Zoom In">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35M11 8v6M8 11h6"/>
        </svg>
      </button>
      <button @click="zoomOut" class="control-btn" title="Zoom Out">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35M8 11h6"/>
        </svg>
      </button>
      <button @click="fitToView" class="control-btn" title="Fit to View">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
        </svg>
      </button>
      <button @click="toggleFullscreen" class="control-btn" :title="isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'">
        <svg v-if="!isFullscreen" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M8 3H5a2 2 0 00-2 2v3M21 8V5a2 2 0 00-2-2h-3M3 16v3a2 2 0 002 2h3M16 21h3a2 2 0 002-2v-3"/>
        </svg>
        <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 14h6v6M20 10h-6V4M14 10l7-7M3 21l7-7"/>
        </svg>
      </button>
    </div>

    <!-- Close button for fullscreen mode -->
    <button v-if="isFullscreen" @click="toggleFullscreen" class="close-fullscreen-btn" title="Exit Fullscreen (Esc)">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 6L6 18M6 6l12 12"/>
      </svg>
    </button>

    <!-- Legend -->
    <div class="legend">
      <div class="legend-items">
        <div class="legend-item">
          <span class="legend-dot primary" style="background-color: #3b82f6;"></span>
          <span>Case Subject</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot" style="background-color: #f87171;"></span>
          <span>Flagged User</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot" style="background-color: #4ade80;"></span>
          <span>Device</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot" style="background-color: #fb923c;"></span>
          <span>IP Address</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot" style="background-color: #c084fc;"></span>
          <span>Stock</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  graphData: {
    type: Object,
    default: () => ({ nodes: [], edges: [] })
  },
  primaryUserId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['askAbout', 'fullscreenChange'])

// Refs
const chartRef = ref(null)
const containerRef = ref(null)
const isFullscreen = ref(false)
const currentZoom = ref(1)

// Node type color configuration
const nodeConfig = {
  user: {
    color: '#22d3ee', // cyan-400 - default user color
    borderColor: '#06b6d4', // cyan-500
    size: 45,
    symbol: 'circle'
  },
  user_primary: {
    color: '#3b82f6', // blue-500 - primary case subject
    borderColor: '#1d4ed8', // blue-700
    size: 55, // larger to stand out
    symbol: 'circle'
  },
  user_flagged: {
    color: '#f87171', // red-400 - flagged/suspicious users
    borderColor: '#dc2626', // red-600
    size: 45,
    symbol: 'circle'
  },
  device: {
    color: '#4ade80', // green-400
    borderColor: '#22c55e', // green-500
    size: 35,
    symbol: 'circle'
  },
  ip: {
    color: '#fb923c', // orange-400
    borderColor: '#f97316', // orange-500
    size: 50,
    symbol: 'circle'
  },
  stock: {
    color: '#c084fc', // purple-400
    borderColor: '#a855f7', // purple-500
    size: 45,
    symbol: 'diamond'
  },
  session: {
    color: '#f472b6', // pink-400
    borderColor: '#ec4899', // pink-500
    size: 30,
    symbol: 'circle'
  }
}

// Edge type color configuration
const edgeConfig = {
  user_ip_event: { color: '#64748b', width: 2 },
  user_device_event: { color: '#64748b', width: 2 },
  user_stock_relation: { color: '#8b5cf6', width: 2.5 }
}

// Zoom functions using dispatchAction for graph series
function zoomIn() {
  if (!chartRef.value) return
  const zoomFactor = 1.4
  currentZoom.value = Math.min(currentZoom.value * zoomFactor, 5)
  chartRef.value.dispatchAction({
    type: 'graphRoam',
    seriesIndex: 0,
    zoom: zoomFactor
  })
}

function zoomOut() {
  if (!chartRef.value) return
  const zoomFactor = 1 / 1.4
  currentZoom.value = Math.max(currentZoom.value * zoomFactor, 0.2)
  chartRef.value.dispatchAction({
    type: 'graphRoam',
    seriesIndex: 0,
    zoom: zoomFactor
  })
}

function fitToView() {
  if (!chartRef.value) return
  // Reset by restoring to initial state
  currentZoom.value = 1
  chartRef.value.dispatchAction({
    type: 'restore'
  })
}

// Handle user's manual zoom/pan via mouse wheel
function handleGraphRoam(params) {
  if (params.zoom) {
    currentZoom.value = Math.min(Math.max(currentZoom.value * params.zoom, 0.2), 5)
  }
}

function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value

  // Emit fullscreen state change to parent
  emit('fullscreenChange', isFullscreen.value)

  if (isFullscreen.value) {
    // Prevent body scroll when fullscreen
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }

  // Trigger chart resize after transition
  setTimeout(() => {
    if (chartRef.value) {
      chartRef.value.resize()
    }
  }, 100)
}

// Handle Escape key to exit fullscreen
function handleKeydown(e) {
  if (e.key === 'Escape' && isFullscreen.value) {
    toggleFullscreen()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})

const handleChartClick = (params) => {
  if (params.dataType === 'node' && params.data) {
    // Node click
    emit('askAbout', {
      type: 'network-node',
      nodeType: params.data.nodeType,
      nodeId: params.data.id,
      label: params.data.name,
      data: params.data.nodeData
    })
  } else if (params.dataType === 'edge' && params.data) {
    // Edge click
    emit('askAbout', {
      type: 'network-edge',
      relation: params.data.relation,
      source: params.data.source,
      target: params.data.target,
      eventType: params.data.eventType,
      data: params.data.edgeData
    })
  }
}

const chartOption = computed(() => {
  const graphData = props.graphData

  if (!graphData.nodes || graphData.nodes.length === 0) {
    return {
      backgroundColor: '#0f172a',
      title: {
        text: 'No network data available',
        left: 'center',
        top: 'center',
        textStyle: { color: '#64748b', fontSize: 14 }
      }
    }
  }

  // Transform nodes for ECharts
  const nodes = graphData.nodes.map((node, index) => {
    // Determine the appropriate config for user nodes
    let configKey = node.type
    if (node.type === 'user') {
      const userId = node.data?.user_id || node.id.split(':')[1]
      if (userId === props.primaryUserId) {
        configKey = 'user_primary' // Primary case subject - blue
      } else {
        configKey = 'user_flagged' // Other users in the ring - red
      }
    }
    const config = nodeConfig[configKey] || nodeConfig.user

    return {
      id: node.id,
      name: node.label || node.id.split(':')[1],
      symbolSize: config.size,
      symbol: config.symbol,
      nodeType: node.type,
      nodeData: node.data,
      isPrimary: configKey === 'user_primary',
      itemStyle: {
        color: config.color,
        borderColor: config.borderColor,
        borderWidth: configKey === 'user_primary' ? 4 : 2, // Thicker border for primary
        shadowBlur: configKey === 'user_primary' ? 20 : 10, // More glow for primary
        shadowColor: config.color + '80'
      },
      label: {
        show: true,
        position: 'right',
        formatter: '{b}',
        fontSize: 11,
        color: '#e2e8f0',
        distance: 8
      }
    }
  })

  // Transform edges for ECharts
  const links = graphData.edges.map((edge, index) => {
    const config = edgeConfig[edge.relation] || { color: '#475569', width: 1.5 }
    return {
      source: edge.source,
      target: edge.target,
      relation: edge.relation,
      eventType: edge.event_type,
      edgeData: edge.data,
      lineStyle: {
        color: config.color,
        width: config.width,
        curveness: 0.1,
        opacity: 0.7
      },
      emphasis: {
        lineStyle: {
          width: config.width + 2,
          opacity: 1
        }
      },
      symbol: ['none', 'arrow'],
      symbolSize: [0, 8]
    }
  })

  return {
    backgroundColor: '#0f172a', // slate-900
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1e293b',
      borderColor: '#334155',
      borderWidth: 1,
      textStyle: { color: '#e2e8f0' },
      extraCssText: 'box-shadow: 0 4px 20px rgba(0,0,0,0.4);',
      formatter: (params) => {
        if (params.dataType === 'node') {
          const node = params.data
          const isPrimary = node.isPrimary
          // Get the correct color based on node type
          let tooltipColor = node.itemStyle?.color || '#22d3ee'
          let typeLabel = node.nodeType.toUpperCase()

          if (node.nodeType === 'user') {
            typeLabel = isPrimary ? 'CASE SUBJECT' : 'FLAGGED USER'
          }

          let content = `
            <div style="padding: 4px 0;">
              <div style="font-weight: 600; color: ${tooltipColor}; margin-bottom: 6px; text-transform: uppercase; font-size: 10px; letter-spacing: 0.5px;">
                ${typeLabel}
              </div>
              <div style="font-size: 14px; font-weight: 500; margin-bottom: 8px;">${node.name}</div>
          `

          if (node.nodeData) {
            if (node.nodeType === 'user') {
              content += `
                <div style="font-size: 11px; color: #94a3b8;">
                  ${isPrimary ? '<div style="color: #3b82f6; font-weight: 600;">Primary Investigation Target</div>' : '<div style="color: #f87171; font-weight: 600;">Connected Account (Suspicious)</div>'}
                  <div>Account: ${node.nodeData.account_id || 'N/A'}</div>
                  <div>Country: ${node.nodeData.nationality || 'N/A'}</div>
                  <div>Occupation: ${node.nodeData.occupation || 'N/A'}</div>
                  <div>Deposit: $${(node.nodeData.account_deposit || 0).toLocaleString()}</div>
                </div>
              `
            } else if (node.nodeType === 'ip') {
              const geo = node.nodeData.geo || {}
              content += `
                <div style="font-size: 11px; color: #94a3b8;">
                  <div>Location: ${geo.city || 'Unknown'}, ${geo.country || 'Unknown'}</div>
                  <div>ASN: ${node.nodeData.asn || 'N/A'}</div>
                  <div>VPN: ${node.nodeData.vpn_suspected ? 'Suspected' : 'No'}</div>
                  <div>Connections: ${node.nodeData.connection_count || 0}</div>
                </div>
              `
            } else if (node.nodeType === 'stock') {
              content += `
                <div style="font-size: 11px; color: #94a3b8;">
                  <div>Total Volume: $${(node.nodeData.total_volume || 0).toLocaleString()}</div>
                  <div>Trade Count: ${node.nodeData.trade_count || 0}</div>
                </div>
              `
            }
          }

          content += `<div style="font-size: 10px; color: #64748b; margin-top: 8px; text-align: center; border-top: 1px solid #334155; padding-top: 6px;">Click to ask AI SENTINEL</div></div>`
          return content
        } else if (params.dataType === 'edge') {
          const edge = params.data
          const relationLabel = edge.relation.replace(/_/g, ' ').toUpperCase()
          let content = `
            <div style="padding: 4px 0;">
              <div style="font-weight: 600; color: #8b5cf6; margin-bottom: 6px; font-size: 10px; letter-spacing: 0.5px;">
                ${relationLabel}
              </div>
              <div style="font-size: 12px; margin-bottom: 6px;">
                <span style="color: #22d3ee;">${edge.source.split(':')[1]}</span>
                <span style="color: #64748b;"> → </span>
                <span style="color: ${nodeConfig[edge.target.split(':')[0]]?.color || '#e2e8f0'}">${edge.target.split(':')[1]}</span>
              </div>
          `

          if (edge.edgeData) {
            content += `
              <div style="font-size: 11px; color: #94a3b8;">
                <div>Event: ${edge.eventType?.toUpperCase() || 'N/A'}</div>
                <div>Amount: $${(edge.edgeData.amount || 0).toLocaleString()}</div>
                ${edge.edgeData.stock_id ? `<div>Stock: ${edge.edgeData.stock_id}</div>` : ''}
              </div>
            `
          }

          content += `<div style="font-size: 10px; color: #64748b; margin-top: 8px; text-align: center; border-top: 1px solid #334155; padding-top: 6px;">Click to ask AI SENTINEL</div></div>`
          return content
        }
        return ''
      }
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: nodes,
        links: links,
        roam: true,
        draggable: true,
        zoom: currentZoom.value,
        force: {
          repulsion: 400,
          gravity: 0.1,
          edgeLength: [80, 200],
          friction: 0.6
        },
        emphasis: {
          focus: 'adjacency',
          blurScope: 'coordinateSystem',
          lineStyle: {
            width: 4
          }
        },
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: [0, 10],
        cursor: 'pointer',
        scaleLimit: {
          min: 0.2,
          max: 5
        }
      }
    ],
    animation: true,
    animationDuration: 1500,
    animationEasingUpdate: 'quinticInOut'
  }
})
</script>

<style scoped>
.network-graph-container {
  width: 100%;
  background: #0f172a;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.network-graph-container.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  border-radius: 0;
}

.chart {
  width: 100%;
  height: 400px;
  cursor: pointer;
}

.fullscreen .chart {
  height: calc(100vh - 60px);
}

/* Control buttons */
.controls {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  z-index: 10;
}

.control-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 6px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s ease;
}

.control-btn:hover {
  background: #334155;
  color: #e2e8f0;
  border-color: #475569;
}

.control-btn:active {
  transform: scale(0.95);
}

/* Close fullscreen button */
.close-fullscreen-btn {
  position: absolute;
  top: 16px;
  left: 16px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #dc2626;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  z-index: 10;
  transition: all 0.2s ease;
}

.close-fullscreen-btn:hover {
  background: #b91c1c;
  transform: scale(1.05);
}

/* Legend */
.legend {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 12px;
  background: #1e293b;
  border-top: 1px solid #334155;
}

.legend-items {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #94a3b8;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  box-shadow: 0 0 8px currentColor;
}

.legend-dot.primary {
  width: 14px;
  height: 14px;
  border: 2px solid #1d4ed8;
  box-shadow: 0 0 12px #3b82f6;
}

.fullscreen .legend {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}
</style>
