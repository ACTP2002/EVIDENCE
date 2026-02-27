<template>
  <div class="event-timeline-container">
    <ClientOnly>
      <VChart :option="chartOption" autoresize class="chart" @click="handleChartClick" />
      <template #fallback>
        <div class="flex items-center justify-center h-full">
          <div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
      </template>
    </ClientOnly>
    <!-- Dynamic Legend -->
    <div class="legend" v-if="legendItems.length > 0">
      <div
        v-for="item in legendItems"
        :key="item.type"
        class="legend-item"
      >
        <svg class="legend-shape" width="12" height="12" viewBox="0 0 12 12">
          <!-- Triangle for alerts -->
          <polygon v-if="item.symbol === 'triangle'"
            points="6,1 11,11 1,11"
            :fill="item.color" />
          <!-- Circle for transactions -->
          <circle v-else-if="item.symbol === 'circle'"
            cx="6" cy="6" r="5"
            :fill="item.color" />
          <!-- Diamond for logins -->
          <polygon v-else-if="item.symbol === 'diamond'"
            points="6,1 11,6 6,11 1,6"
            :fill="item.color" />
          <!-- Pin for password change -->
          <g v-else-if="item.symbol === 'pin'">
            <circle cx="6" cy="4" r="3" :fill="item.color" />
            <polygon points="6,7 8,11 4,11" :fill="item.color" />
          </g>
          <!-- Default square -->
          <rect v-else x="1" y="1" width="10" height="10" rx="2" :fill="item.color" />
        </svg>
        <span>{{ item.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  alerts: {
    type: Array,
    default: () => []
  },
  transactions: {
    type: Array,
    default: () => []
  },
  logins: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['askAbout'])

const handleChartClick = (params) => {
  if (params.data && params.data.eventData) {
    emit('askAbout', {
      type: 'timeline',
      eventType: params.data.eventData.type,
      event: params.data.eventData
    })
  }
}

// Event type configs - extended for dynamic legend
const eventConfig = {
  alert: { color: '#DC2626', symbol: 'triangle', yPos: 3, label: 'Alert' },
  transaction: { color: '#3B82F6', symbol: 'circle', yPos: 2, label: 'Transaction' },
  login: { color: '#8B5CF6', symbol: 'diamond', yPos: 1, label: 'Login' },
  login_success: { color: '#10B981', symbol: 'diamond', yPos: 1, label: 'Login (Success)' },
  login_failed: { color: '#F59E0B', symbol: 'diamond', yPos: 1, label: 'Login (Failed)' },
  password_change: { color: '#EC4899', symbol: 'pin', yPos: 1, label: 'Password Change' }
}

// Process and merge all events
const timelineEvents = computed(() => {
  const events = []

  // Add alerts
  if (props.alerts && Array.isArray(props.alerts)) {
    props.alerts.forEach(alert => {
      if (alert.event_time) {
        events.push({
          type: 'alert',
          time: new Date(alert.event_time),
          label: alert.signal || alert.detector_type || 'Alert',
          severity: alert.severity,
          id: alert.alert_id,
          raw: alert
        })
      }
    })
  }

  // Add transactions
  if (props.transactions && Array.isArray(props.transactions)) {
    props.transactions.forEach(txn => {
      if (txn.event_time) {
        const amount = txn.data?.amount || 0
        const type = txn.event_type || 'transaction'
        events.push({
          type: 'transaction',
          time: new Date(txn.event_time),
          label: `${type.toUpperCase()} $${Math.abs(amount).toLocaleString()}`,
          amount: amount,
          id: txn.event_id,
          raw: txn
        })
      }
    })
  }

  // Add logins and auth events
  if (props.logins && Array.isArray(props.logins)) {
    props.logins.forEach(login => {
      if (login.event_time) {
        const country = login.data?.geo?.country || 'Unknown'
        const isSuccess = login.data?.success === true
        const eventType = login.event_type || 'login_attempt'

        // Determine specific event type for coloring
        let type = 'login'
        let label = `Login from ${country}`

        if (eventType === 'password_change') {
          type = 'password_change'
          label = `Password changed from ${country}`
        } else if (isSuccess) {
          type = 'login_success'
          label = `Login from ${country} (Success)`
        } else {
          type = 'login_failed'
          const reason = login.data?.failure_reason || 'unknown'
          label = `Login from ${country} (Failed: ${reason})`
        }

        events.push({
          type: type,
          time: new Date(login.event_time),
          label: label,
          success: isSuccess,
          id: login.event_id,
          raw: login
        })
      }
    })
  }

  // Sort by time, with priority for important events when close in time
  // Higher priority events render last (on top) when overlapping
  const eventPriority = {
    'login_success': 0,
    'login': 1,
    'transaction': 2,
    'login_failed': 3,
    'password_change': 4,
    'alert': 5
  }

  return events.sort((a, b) => {
    const timeDiff = a.time - b.time
    // If events are more than 10 minutes apart, sort by time only
    if (Math.abs(timeDiff) > 10 * 60 * 1000) return timeDiff
    // For close events, sort by priority (important events render last = on top)
    const priorityDiff = (eventPriority[a.type] || 0) - (eventPriority[b.type] || 0)
    if (priorityDiff !== 0) return priorityDiff
    // Same priority, sort by time
    return timeDiff
  })
})

// Dynamic legend based on actual events present
const legendItems = computed(() => {
  const events = timelineEvents.value
  const presentTypes = new Set(events.map(e => e.type))

  // Define display order
  const displayOrder = ['alert', 'transaction', 'login_success', 'login_failed', 'password_change', 'login']

  const items = []
  for (const type of displayOrder) {
    if (presentTypes.has(type)) {
      const config = eventConfig[type]
      items.push({
        type: type,
        color: config.color,
        label: config.label,
        symbol: config.symbol
      })
    }
  }

  return items
})

const chartOption = computed(() => {
  const events = timelineEvents.value

  if (events.length === 0) {
    return {
      title: {
        text: 'No timeline events',
        left: 'center',
        top: 'center',
        textStyle: { color: '#94a3b8', fontSize: 14 }
      }
    }
  }

  // Create scatter data points
  const data = events.map((event, idx) => {
    const config = eventConfig[event.type]
    return {
      value: [event.time.getTime(), config.yPos],
      eventData: event,
      itemStyle: {
        color: config.color
      },
      symbol: config.symbol,
      symbolSize: event.type === 'alert' ? 16 : 12
    }
  })

  // Get time range
  const times = events.map(e => e.time.getTime())
  const minTime = Math.min(...times)
  const maxTime = Math.max(...times)
  const padding = (maxTime - minTime) * 0.1 || 3600000 // 1 hour padding if same time

  return {
    toolbox: {
      show: true,
      right: 10,
      top: -5,
      itemSize: 18,
      itemGap: 12,
      feature: {
        dataZoom: {
          yAxisIndex: 'none',
          title: { zoom: 'Zoom Select', back: 'Undo Zoom' },
          icon: {
            zoom: 'path://M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14zM12 10h-2v2H9v-2H7V9h2V7h1v2h2v1z',
            back: 'path://M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z'
          }
        },
        restore: {
          title: 'Reset View',
          icon: 'path://M17.65 6.35A7.958 7.958 0 0 0 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0 1 12 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z'
        }
      },
      iconStyle: {
        borderColor: '#475569',
        borderWidth: 1.5
      },
      emphasis: {
        iconStyle: {
          borderColor: '#3b82f6'
        }
      }
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: 0,
        bottom: 10,
        height: 25,
        borderColor: '#94a3b8',
        backgroundColor: '#f1f5f9',
        fillerColor: 'rgba(59, 130, 246, 0.2)',
        handleStyle: {
          color: '#3b82f6',
          borderColor: '#3b82f6'
        },
        dataBackground: {
          lineStyle: { color: '#94a3b8' },
          areaStyle: { color: '#e2e8f0' }
        },
        selectedDataBackground: {
          lineStyle: { color: '#3b82f6' },
          areaStyle: { color: 'rgba(59, 130, 246, 0.2)' }
        },
        textStyle: { color: '#475569', fontSize: 10 },
        brushSelect: false
      },
      {
        type: 'inside',
        xAxisIndex: 0,
        zoomOnMouseWheel: true,
        moveOnMouseMove: true,
        moveOnMouseWheel: false
      }
    ],
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const event = params.data.eventData
        const config = eventConfig[event.type]
        const time = event.time.toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })

        let content = `
          <div style="font-weight: 600; margin-bottom: 4px; color: ${config.color}">
            ${config.label}
          </div>
          <div style="font-size: 13px; margin-bottom: 4px;">${event.label}</div>
          <div style="font-size: 11px; color: #64748b;">${time}</div>
        `

        if (event.type === 'alert' && event.severity) {
          content += `<div style="font-size: 11px; margin-top: 4px;">Severity: <strong>${event.severity}</strong></div>`
        }

        // Show risk hints for failed logins
        if (event.type === 'login_failed' && event.raw?.data?.risk_hint && event.raw.data.risk_hint !== 'na') {
          content += `<div style="font-size: 11px; margin-top: 4px; color: #F59E0B;">Risk: <strong>${event.raw.data.risk_hint.replace(/_/g, ' ')}</strong></div>`
        }

        content += `<div style="font-size: 10px; color: #94a3b8; margin-top: 8px; text-align: center;">Click to ask AI SENTINEL</div>`

        return content
      },
      backgroundColor: 'white',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      textStyle: { color: '#1e293b' },
      extraCssText: 'box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);'
    },
    grid: {
      left: '3%',
      right: '3%',
      top: '10%',
      bottom: '25%',
      containLabel: true
    },
    xAxis: {
      type: 'time',
      min: minTime - padding,
      max: maxTime + padding,
      axisLine: {
        lineStyle: { color: '#e5e7eb' }
      },
      axisLabel: {
        color: '#64748b',
        fontSize: 10,
        formatter: (value) => {
          const date = new Date(value)
          return date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
        }
      },
      splitLine: {
        show: true,
        lineStyle: { color: '#f1f5f9', type: 'dashed' }
      }
    },
    yAxis: {
      type: 'category',
      data: ['', 'Login', 'Transaction', 'Alert'],
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: '#475569',
        fontSize: 11,
        fontWeight: 500
      },
      splitLine: { show: false }
    },
    series: [
      {
        type: 'scatter',
        data: data,
        emphasis: {
          scale: 1.5
        }
      }
    ],
    animation: true,
    animationDuration: 600
  }
})
</script>

<style scoped>
.event-timeline-container {
  width: 100%;
}

.chart {
  width: 100%;
  height: 280px;
  cursor: pointer;
}

.legend {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px 20px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e5e7eb;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #64748b;
}

.legend-shape {
  flex-shrink: 0;
}
</style>
