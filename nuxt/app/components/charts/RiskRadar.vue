<template>
  <div class="risk-radar-container">
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
  status: {
    type: Object,
    default: () => ({})
  },
  profile: {
    type: Object,
    default: () => ({})
  },
  caseScore: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['askAbout'])

const handleChartClick = (params) => {
  if (params.data && params.name) {
    emit('askAbout', {
      type: 'radar',
      category: params.name,
      value: params.value
    })
  }
}

// Calculate risk scores for each dimension (0-100 scale)
const riskDimensions = computed(() => {
  const status = props.status || {}
  const profile = props.profile || {}
  const txn = status.txn || {}
  const auth = status.auth || {}
  const network = status.network || {}
  const kyc = profile.kyc || {}
  const risk = profile.risk || {}

  // 1. Income Deviation Risk
  const declaredIncome = parseFloat(kyc.income) || 1
  const amountOut30d = txn.amount_out_30d || 0
  const incomeRatio = amountOut30d / declaredIncome
  const incomeRisk = Math.min(100, incomeRatio * 10) // 10x income = 100% risk

  // 2. Velocity Risk (transaction frequency + new devices/IPs)
  const txnCount1d = txn.count_1d || 0
  const newDevice = auth.new_device_1d || 0
  const newIp = auth.new_ip_1d || 0
  const velocityRisk = Math.min(100, (txnCount1d * 10) + (newDevice * 30) + (newIp * 20))

  // 3. Network Risk (unique IPs, geo changes, latency anomalies)
  const uniqueIps = network.unique_ip_5m || 0
  const geoChange = network.geo_change_1d || 0
  const packetLoss = network.packet_loss_5m || 0
  const networkRisk = Math.min(100, (uniqueIps * 15) + (geoChange * 40) + (packetLoss * 10))

  // 4. KYC Risk (based on verification level, age patterns)
  const age = parseInt(kyc.age) || 30
  const kycLevel = kyc.kyc_level || 'tier_1'
  const ageRisk = age > 60 ? 20 : (age < 25 ? 15 : 0) // Elderly or very young
  const kycLevelRisk = kycLevel === 'tier_1' ? 10 : (kycLevel === 'tier_2' ? 5 : 0)
  const kycRisk = Math.min(100, ageRisk + kycLevelRisk + (incomeRatio > 5 ? 50 : 0))

  // 5. Behavioral Risk (based on case score)
  const behavioralRisk = props.caseScore || 0

  // 6. Identity Risk (PEP, sanctions, adverse media)
  const pepFlag = risk.pep_flag ? 40 : 0
  const sanctionsFlag = risk.sanctions_status === 'true' || risk.sanctions_status === true ? 60 : 0
  const adverseMedia = risk.adverse_media_flag ? 30 : 0
  const identityRisk = Math.min(100, pepFlag + sanctionsFlag + adverseMedia)

  return {
    'Income Deviation': Math.round(incomeRisk),
    'Velocity': Math.round(velocityRisk),
    'Network': Math.round(networkRisk),
    'KYC': Math.round(kycRisk),
    'Behavioral': Math.round(behavioralRisk),
    'Identity': Math.round(identityRisk)
  }
})

const chartOption = computed(() => {
  const dimensions = riskDimensions.value
  const categories = Object.keys(dimensions)
  const values = Object.values(dimensions)

  // Create baseline comparison (normal user ~20% across all dimensions)
  const normalBaseline = categories.map(() => 20)

  return {
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.seriesName === 'Current Case') {
          const idx = params.dataIndex
          const category = categories[idx]
          const value = values[idx]
          return `
            <div style="font-weight: 600; margin-bottom: 4px;">${category}</div>
            <div style="font-size: 18px; font-weight: 700; color: ${value >= 60 ? '#DC2626' : value >= 40 ? '#F59E0B' : '#10B981'}">
              ${value}%
            </div>
            <div style="font-size: 11px; color: #64748b; margin-top: 4px;">
              Click to ask AI SENTINEL
            </div>
          `
        }
        return ''
      },
      backgroundColor: 'white',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      textStyle: { color: '#1e293b' },
      extraCssText: 'box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);'
    },
    legend: {
      data: ['Current Case', 'Normal Baseline'],
      bottom: 0,
      textStyle: {
        fontSize: 11,
        color: '#64748b'
      },
      itemWidth: 14,
      itemHeight: 14
    },
    radar: {
      indicator: categories.map(cat => ({
        name: cat,
        max: 100
      })),
      center: ['50%', '45%'],
      radius: '65%',
      axisName: {
        color: '#475569',
        fontSize: 10
      },
      splitNumber: 4,
      splitArea: {
        areaStyle: {
          color: ['#fff', '#f8fafc', '#fff', '#f8fafc']
        }
      },
      axisLine: {
        lineStyle: {
          color: '#e2e8f0'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#e2e8f0'
        }
      }
    },
    series: [
      {
        name: 'Current Case',
        type: 'radar',
        data: [
          {
            value: values,
            name: 'Current Case',
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {
              color: '#DC2626',
              width: 2
            },
            areaStyle: {
              color: 'rgba(220, 38, 38, 0.15)'
            },
            itemStyle: {
              color: '#DC2626'
            }
          }
        ]
      },
      {
        name: 'Normal Baseline',
        type: 'radar',
        data: [
          {
            value: normalBaseline,
            name: 'Normal Baseline',
            symbol: 'circle',
            symbolSize: 4,
            lineStyle: {
              color: '#10B981',
              width: 1,
              type: 'dashed'
            },
            areaStyle: {
              color: 'rgba(16, 185, 129, 0.05)'
            },
            itemStyle: {
              color: '#10B981'
            }
          }
        ]
      }
    ],
    animation: true,
    animationDuration: 800
  }
})
</script>

<style scoped>
.risk-radar-container {
  width: 100%;
  height: 320px;
}

.chart {
  width: 100%;
  height: 100%;
  cursor: pointer;
}
</style>
