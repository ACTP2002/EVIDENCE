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
                                <div class="flex flex-col gap-1.5">
                                    <div v-for="(reason, idx) in case_.topReasons.slice(0, 2)" :key="idx"
                                        class="flex items-center gap-2 text-[13px] text-slate-500">
                                        <div class="w-1 h-1 rounded-full bg-slate-300 flex-shrink-0"></div>
                                        {{ reason.text }}
                                        <span class="font-mono font-semibold text-slate-900 text-xs">{{ reason.value
                                            }}</span>
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
import { ref, computed } from 'vue'
import { getRiskLevel, getRiskStatistics } from '~/utils/riskAssessment'

const activeFilter = ref('all')

const filters = [
    { id: 'all', label: 'All Cases', count: null }, // Will be computed
    { id: 'high-risk', label: 'High Risk', count: null },
    { id: 'open', label: 'Open', count: null },
    { id: 'confirmed', label: 'Confirmed Fraud', count: null }
]

const cases = ref([
    {
        id: 'FR-2024-0847',
        riskScore: 94,
        topReasons: [
            { text: 'Deposits exceed declared income by', value: '1,420%' },
            { text: 'VPN access from sanctioned jurisdiction', value: '73% of logins' }
        ],
        client: { name: 'Marcus Chen', id: 'CL-48291' },
        flaggedTime: '2 hours ago',
        flaggedDate: 'Feb 7, 2026',
        status: 'Open'
    },
    {
        id: 'FR-2024-0846',
        riskScore: 91,
        topReasons: [
            { text: 'AI-generated face detected in verification', value: '98% confidence' },
            { text: 'Device fingerprint matches', value: '7 flagged accounts' }
        ],
        client: { name: 'Elena Rodriguez', id: 'CL-59284' },
        flaggedTime: '3 hours ago',
        flaggedDate: 'Feb 7, 2026',
        status: 'Open'
    },
    {
        id: 'FR-2024-0845',
        riskScore: 87,
        topReasons: [
            { text: 'Rapid deposit-withdrawal cycle detected', value: '$24K in 48hrs' },
            { text: 'Transaction pattern matches known ML network', value: '12 confirmed cases' }
        ],
        client: { name: 'David Kim', id: 'CL-73849' },
        flaggedTime: '5 hours ago',
        flaggedDate: 'Feb 7, 2026',
        status: 'Under Review'
    },
    {
        id: 'FR-2024-0844',
        riskScore: 33,
        topReasons: [
            { text: 'Synthetic identity indicators', value: '5 data inconsistencies' },
            { text: 'Login from geographically impossible location', value: '2,400 km in 3 hrs' }
        ],
        client: { name: 'Sarah O\'Brien', id: 'CL-29384' },
        flaggedTime: '8 hours ago',
        flaggedDate: 'Feb 7, 2026',
        status: 'Open'
    },
    {
        id: 'FR-2024-0843',
        riskScore: 50,
        topReasons: [
            { text: 'Document verification failed', value: 'Forged passport detected' },
            { text: 'Email domain associated with fraud network', value: '23 flagged accounts' }
        ],
        client: { name: 'Ahmed Hassan', id: 'CL-84729' },
        flaggedTime: '12 hours ago',
        flaggedDate: 'Feb 6, 2026',
        status: 'Open'
    }
])

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
    navigateTo(`/cases/${caseId}`)
}

const openCase = (caseId) => {
    navigateTo(`/cases/${caseId}`)
}
</script>