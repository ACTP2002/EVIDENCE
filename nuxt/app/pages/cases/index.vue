<!-- cases/index.vue -->
<template>
    <div class="min-h-screen bg-gray-50">
        <!-- Page Header -->
        <header class="bg-white border-b border-gray-200 px-10 py-8">
            <div class="max-w-[1600px] mx-auto flex justify-between items-start">
                <div class="flex-1">
                    <h1 class="text-[28px] font-bold text-slate-900 mb-1.5 tracking-tight">Case Inbox</h1>
                    <p class="text-sm text-slate-500 font-medium">AI-prioritized fraud alerts requiring investigation
                    </p>
                </div>
                <div class="flex gap-4">
                    <div class="bg-gray-50 border border-red-200 rounded-lg px-6 py-4 text-center min-w-[100px]">
                        <div class="text-[32px] font-bold font-mono leading-none mb-1 text-risk-critical">{{
                            stats.critical }}</div>
                        <div class="text-[11px] uppercase tracking-wider font-semibold text-slate-400">Critical</div>
                    </div>
                    <div class="bg-gray-50 border border-orange-200 rounded-lg px-6 py-4 text-center min-w-[100px]">
                        <div class="text-[32px] font-bold font-mono leading-none mb-1 text-risk-high">{{ stats.high }}
                        </div>
                        <div class="text-[11px] uppercase tracking-wider font-semibold text-slate-400">High Risk</div>
                    </div>
                    <div class="bg-gray-50 border border-blue-200 rounded-lg px-6 py-4 text-center min-w-[100px]">
                        <div class="text-[32px] font-bold font-mono leading-none mb-1 text-status-open">{{
                            openCasesCount }}</div>
                        <div class="text-[11px] uppercase tracking-wider font-semibold text-slate-400">Open Cases</div>
                    </div>
                </div>
            </div>
        </header>

        <!-- Page Content -->
        <div class="max-w-[1600px] mx-auto px-10 py-6">
            <!-- Controls Bar -->
            <div class="flex justify-between items-center mb-5">
                <div class="flex gap-2">
                    <button v-for="filter in computedFilters" :key="filter.id" :class="[
                        'px-4 py-2.5 bg-white border rounded-lg text-sm font-medium transition-all flex items-center gap-2',
                        activeFilter === filter.id
                            ? 'bg-primary border-primary text-slate-900'
                            : 'border-gray-200 text-slate-500 hover:border-gray-300 hover:text-slate-900'
                    ]" @click="activeFilter = filter.id">
                        {{ filter.label }}
                        <span v-if="filter.count" :class="[
                            'px-2 py-0.5 rounded-full text-xs font-mono font-semibold',
                            activeFilter === filter.id ? 'bg-white/20' : 'bg-black/10'
                        ]">
                            {{ filter.count }}
                        </span>
                    </button>
                </div>

                <div class="flex gap-2">
                    <button
                        class="px-4 py-2.5 bg-white border border-gray-200 rounded-lg text-sm font-medium text-slate-500 hover:border-gray-300 hover:text-slate-900 transition-all flex items-center gap-2">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M2 5H14M5 8H11M7 11H9" stroke="currentColor" stroke-width="1.5"
                                stroke-linecap="round" />
                        </svg>
                        Filter
                    </button>
                    <button
                        class="px-4 py-2.5 bg-white border border-gray-200 rounded-lg text-sm font-medium text-slate-500 hover:border-gray-300 hover:text-slate-900 transition-all flex items-center gap-2">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M3 8H13M8 3V13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                        </svg>
                        Export
                    </button>
                </div>
            </div>

            <!-- Cases Table -->
            <div class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm-custom">
                <table class="w-full border-collapse">
                    <thead>
                        <tr class="bg-gray-50 border-b border-gray-200">
                            <th
                                class="text-left px-4 py-3.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                                Case ID</th>
                            <th
                                class="text-left px-4 py-3.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                                Risk Score</th>
                            <th
                                class="text-left px-4 py-3.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                                Risk Level</th>
                            <th
                                class="text-left px-4 py-3.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                                Top Reasons Flagged</th>
                            <th
                                class="text-left px-4 py-3.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                                Client</th>
                            <th
                                class="text-left px-4 py-3.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                                Flagged</th>
                            <th
                                class="text-left px-4 py-3.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                                Status</th>
                            <th class="px-4 py-3.5"></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(case_, idx) in filteredCases" :key="case_.id"
                            class="border-b border-gray-200 last:border-b-0 cursor-pointer hover:bg-gray-50 transition-colors animate-fade-in"
                            :style="{ animationDelay: `${idx * 0.05}s` }" @click="navigateToCase(case_.id)">
                            <td class="px-4 py-4">
                                <div class="font-mono font-semibold text-slate-900 text-[13px]">{{ case_.id }}</div>
                            </td>

                            <td class="px-4 py-4">
                                <div class="flex items-center gap-3">
                                    <div :class="[
                                        'font-mono font-bold text-xl min-w-[40px]',
                                        getRiskLevel(case_.riskScore) === 'Critical' ? 'text-risk-critical' :
                                            getRiskLevel(case_.riskScore) === 'High' ? 'text-risk-high' :
                                                getRiskLevel(case_.riskScore) === 'Medium' ? 'text-risk-medium' :
                                                    'text-risk-low'
                                    ]">
                                        {{ case_.riskScore }}
                                    </div>
                                    <div class="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden max-w-[80px]">
                                        <div :class="[
                                            'h-full rounded-full',
                                            getRiskLevel(case_.riskScore) === 'Critical' ? 'bg-risk-critical' :
                                                getRiskLevel(case_.riskScore) === 'High' ? 'bg-risk-high' :
                                                    getRiskLevel(case_.riskScore) === 'Medium' ? 'bg-risk-medium' :
                                                        'bg-risk-low'
                                        ]" :style="{ width: case_.riskScore + '%' }"></div>
                                    </div>
                                </div>
                            </td>

                            <td class="px-4 py-4">
                                <span :class="[
                                    'inline-flex px-2.5 py-1 rounded-md text-xs font-semibold uppercase tracking-wide',
                                    getRiskLevel(case_.riskScore) === 'Critical' ? 'bg-red-50 text-risk-critical' :
                                        getRiskLevel(case_.riskScore) === 'High' ? 'bg-orange-50 text-risk-high' :
                                            getRiskLevel(case_.riskScore) === 'Medium' ? 'bg-amber-50 text-risk-medium' :
                                                'bg-green-50 text-risk-low'
                                ]">
                                    {{ getRiskLevel(case_.riskScore) }}
                                </span>
                            </td>

                            <td class="px-4 py-4">
                                <div class="flex flex-col gap-2">
                                    <div v-for="(reason, idx) in case_.topReasons.slice(0, 2)" :key="idx"
                                        class="flex items-start justify-between gap-4">
                                        <div class="flex items-start gap-2 text-[13px] text-slate-600 flex-1">
                                            <div class="w-1.5 h-1.5 rounded-full bg-slate-400 flex-shrink-0 mt-1.5"></div>
                                            <span class="leading-snug">{{ reason.text }}</span>
                                        </div>
                                        <div class="flex flex-col items-end flex-shrink-0 min-w-[60px]">
                                            <span class="font-mono font-bold text-slate-900 text-sm">{{ reason.confidence }}</span>
                                            <span class="text-[10px] text-slate-400 uppercase tracking-wide">confidence</span>
                                        </div>
                                    </div>
                                </div>
                            </td>

                            <td class="px-4 py-4">
                                <div class="flex flex-col gap-0.5">
                                    <div class="font-semibold text-slate-900">{{ case_.client.name }}</div>
                                    <div class="text-xs text-slate-400 font-mono">ID: {{ case_.client.id }}</div>
                                </div>
                            </td>

                            <td class="px-4 py-4">
                                <div class="flex flex-col gap-0.5">
                                    <div class="font-medium text-slate-900 text-[13px]">{{ case_.flaggedTime }}</div>
                                    <div class="text-xs text-slate-400">{{ case_.flaggedDate }}</div>
                                </div>
                            </td>

                            <td class="px-4 py-4">
                                <span :class="[
                                    'inline-flex px-2.5 py-1 rounded-md text-xs font-semibold',
                                    case_.status === 'Open' ? 'bg-blue-50 text-status-open' :
                                        case_.status === 'Under Review' ? 'bg-amber-50 text-status-review' :
                                            case_.status === 'Confirmed Fraud' ? 'bg-red-50 text-status-confirmed' :
                                                'bg-green-50 text-status-false'
                                ]">
                                    {{ case_.status }}
                                </span>
                            </td>

                            <td class="px-4 py-4">
                                <button
                                    class="w-8 h-8 rounded-md border border-gray-200 flex items-center justify-center text-slate-400 hover:bg-primary hover:border-primary hover:text-white transition-all"
                                    @click.stop="openCase(case_.id)">
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                        <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.5"
                                            stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getRiskLevel, getRiskStatistics } from '~/utils/riskAssessment'

const { getCases } = useApi()

const activeFilter = ref('all')
const loading = ref(true)
const error = ref(null)

const filters = [
    { id: 'all', label: 'All Cases', count: null }, // Will be computed
    { id: 'high-risk', label: 'High Risk', count: null },
    { id: 'open', label: 'Open', count: null },
    { id: 'confirmed', label: 'Confirmed Fraud', count: null }
]

const cases = ref([])

/**
 * Transform backend case data to frontend format
 */
const transformCase = (backendCase) => {
    // Extract top reasons from alerts - get explanation and confidence separately
    const topReasons = (backendCase.alerts || []).slice(0, 2).map(alert => {
        // Get first evidence explanation or use signal as fallback
        const evidence = alert.evidence?.[0]
        const confidenceVal = parseFloat(alert.confidence) || 0
        const confidencePercent = confidenceVal > 1 ? confidenceVal : Math.round(confidenceVal * 100)

        return {
            text: evidence?.explanation || alert.signal || 'Anomaly detected',
            confidence: `${confidencePercent}%`
        }
    })

    // Format flagged time
    const flaggedDate = new Date(backendCase.opened_at || backendCase.last_updated)
    const now = new Date()
    const hoursAgo = Math.floor((now - flaggedDate) / (1000 * 60 * 60))
    const daysAgo = Math.floor(hoursAgo / 24)
    const flaggedTime = daysAgo > 0 ? `${daysAgo} days ago` : `${hoursAgo} hours ago`

    return {
        id: backendCase.case_id,
        riskScore: backendCase.case_score || 0,
        topReasons: topReasons.length > 0 ? topReasons : [{ text: 'Under investigation', confidence: 'Pending' }],
        client: {
            name: backendCase.user_id || 'Unknown',
            id: backendCase.user_id || 'N/A'
        },
        flaggedTime: flaggedTime,
        flaggedDate: flaggedDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        status: backendCase.status === 'OPEN' ? 'Open' :
                backendCase.status === 'CLOSED' ? 'Closed' :
                backendCase.status === 'ESCALATED' ? 'Under Review' : 'Open'
    }
}

/**
 * Fetch cases from backend API
 */
const fetchCases = async () => {
    loading.value = true
    error.value = null

    try {
        const data = await getCases()
        cases.value = data.map(transformCase)
    } catch (e) {
        console.error('Failed to fetch cases:', e)
        error.value = e.message
        // Fallback to empty array
        cases.value = []
    } finally {
        loading.value = false
    }
}

// Fetch cases on mount
onMounted(() => {
    fetchCases()
})

// Sort cases by risk score (high to low)
const sortedCases = computed(() => {
    return [...cases.value].sort((a, b) => b.riskScore - a.riskScore)
})

// Calculate statistics
const stats = computed(() => getRiskStatistics(sortedCases.value))

// Count open cases
const openCasesCount = computed(() => {
    return sortedCases.value.filter(c => c.status === 'Open').length
})

// Count confirmed fraud cases
const confirmedFraudCount = computed(() => {
    return sortedCases.value.filter(c => c.status === 'Confirmed Fraud').length
})

// High risk count (Critical + High)
const highRiskCount = computed(() => {
    return stats.value.critical + stats.value.high
})

// Update filter counts dynamically
const computedFilters = computed(() => [
    { id: 'all', label: 'All Cases', count: sortedCases.value.length },
    { id: 'high-risk', label: 'High Risk', count: highRiskCount.value },
    { id: 'open', label: 'Open', count: openCasesCount.value },
    { id: 'confirmed', label: 'Confirmed Fraud', count: confirmedFraudCount.value }
])

const filteredCases = computed(() => {
    if (activeFilter.value === 'all') return sortedCases.value
    if (activeFilter.value === 'high-risk') {
        return sortedCases.value.filter(c => {
            const level = getRiskLevel(c.riskScore)
            return level === 'Critical' || level === 'High'
        })
    }
    if (activeFilter.value === 'open') {
        return sortedCases.value.filter(c => c.status === 'Open')
    }
    if (activeFilter.value === 'confirmed') {
        return sortedCases.value.filter(c => c.status === 'Confirmed Fraud')
    }
    return sortedCases.value
})

const navigateToCase = (caseId) => {
    navigateTo(`/cases/${caseId}/investigate`)
}

const openCase = (caseId) => {
    navigateTo(`/cases/${caseId}/investigate`)
}
</script>