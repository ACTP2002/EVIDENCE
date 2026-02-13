<template>
    <div class="flex flex-col h-screen bg-slate-50">
        <!-- Primary Header -->
        <header class="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200">
            <div class="flex items-center gap-4">
                <NuxtLink to="/cases" class="flex items-center gap-1 text-slate-500 hover:text-slate-700 text-sm">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Cases
                </NuxtLink>
                <div class="h-4 w-px bg-gray-200"></div>
                <h1 class="text-base font-semibold text-slate-900">{{ caseData.case_id }}</h1>
                <span :class="getRiskBadgeClass(caseData.risk_level)" class="px-2 py-0.5 text-xs font-semibold rounded">
                    {{ caseData.risk_level.toUpperCase() }} ({{ caseData.risk_score }})
                </span>
            </div>
            <div class="flex items-center gap-3">
                <div class="flex items-center gap-1.5 text-sm text-slate-500">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
                        <path d="M8 5V8L10 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    </svg>
                    SLA: {{ caseData.sla_remaining }}
                </div>
                <button
                    @click="toggleSentinel"
                    class="flex items-center gap-1.5 px-3 py-1.5 text-sm text-slate-600 hover:text-slate-900 border border-gray-200 rounded-md hover:bg-gray-50"
                >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" :class="sentinelVisible ? '' : 'rotate-180'">
                        <path d="M6 4L10 8L6 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    {{ sentinelVisible ? 'Hide SENTINEL' : 'Show SENTINEL' }}
                </button>
            </div>
        </header>

        <!-- Secondary Header - Case Info Bar -->
        <div class="flex items-center justify-between px-4 py-2 bg-white border-b border-gray-200 text-sm">
            <div class="flex items-center gap-6">
                <div class="flex items-center gap-4">
                    <div class="flex items-center gap-1.5">
                        <span class="text-slate-500">Customer:</span>
                        <span class="font-medium text-slate-900">{{ caseData.customer_name }}</span>
                    </div>
                    <div class="h-3 w-px bg-gray-200"></div>
                    <div class="flex items-center gap-1.5">
                        <span class="text-slate-500">Account:</span>
                        <span class="font-medium text-slate-900">{{ caseData.account_id }}</span>
                    </div>
                    <div class="h-3 w-px bg-gray-200"></div>
                    <div class="flex items-center gap-1.5">
                        <span class="text-slate-500">Status:</span>
                        <span class="font-medium text-slate-900">{{ caseData.status }}</span>
                    </div>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <NuxtLink
                    :to="`/cases/${caseId}/report`"
                    class="px-3 py-1.5 text-sm font-medium text-white bg-slate-900 rounded-md hover:bg-slate-800"
                >
                    Generate Report
                </NuxtLink>
                <button class="px-3 py-1.5 text-sm font-medium text-white bg-risk-critical rounded-md hover:bg-red-700">
                    Confirm Fraud
                </button>
                <button class="px-3 py-1.5 text-sm font-medium text-slate-700 border border-gray-200 rounded-md hover:bg-gray-50">
                    False Positive
                </button>
                <button
                    @click="showNotesModal = true"
                    class="px-3 py-1.5 text-sm font-medium text-slate-700 border border-gray-200 rounded-md hover:bg-gray-50"
                >
                    Add Notes
                </button>
            </div>
        </div>

        <!-- Main Content -->
        <div class="flex flex-1 overflow-hidden p-4 gap-4">
            <!-- Loading State -->
            <div v-if="isLoading" class="flex-1 flex items-center justify-center">
                <div class="text-center">
                    <div class="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <div class="text-slate-600">Loading case data...</div>
                </div>
            </div>

            <!-- Error State -->
            <div v-else-if="loadError" class="flex-1 flex items-center justify-center">
                <div class="text-center max-w-md">
                    <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-red-500" viewBox="0 0 24 24" fill="none">
                            <path d="M12 8V12M12 16H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold text-slate-900 mb-2">Failed to Load Case</h3>
                    <p class="text-slate-600 mb-4">{{ loadError }}</p>
                    <button @click="fetchCaseData" class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-light">
                        Try Again
                    </button>
                </div>
            </div>

            <!-- Investigation Panel (Left - Full width when SENTINEL hidden) -->
            <div v-else class="flex-1 flex flex-col gap-4 overflow-hidden">
                <!-- Top Section: Alerts and Risk Breakdown -->
                <div class="flex gap-4">
                    <!-- Alerts Section -->
                    <div class="flex-1 bg-white border border-gray-200 rounded-lg shadow-sm p-4 flex flex-col">
                        <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Alerts</div>
                        <div class="space-y-2 overflow-y-auto max-h-[200px]">
                            <div
                                v-for="alert in alerts"
                                :key="alert.alert_id"
                                class="p-3 border border-gray-200 rounded-lg"
                            >
                                <div class="flex items-center gap-2 mb-1">
                                    <span
                                        :class="getAlertSeverityClass(alert.severity)"
                                        class="px-2 py-0.5 text-xs font-semibold rounded"
                                    >
                                        {{ alert.severity.toUpperCase() }}
                                    </span>
                                    <span class="text-xs text-slate-500">{{ alert.alert_id }}</span>
                                </div>
                                <div class="text-sm text-slate-900 mb-1">{{ alert.description }}</div>
                                <div class="flex items-center gap-3 text-xs text-slate-500">
                                    <span>Source: {{ alert.detector_source }}</span>
                                    <span>{{ formatAlertTime(alert.triggered_at) }}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Risk Breakdown -->
                    <div class="w-[320px] flex-shrink-0 bg-white border border-gray-200 rounded-lg shadow-sm p-4">
                        <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Risk Breakdown</div>
                        <div class="space-y-2.5">
                            <div v-for="risk in riskBreakdown" :key="risk.category" class="flex items-center gap-3">
                                <div class="w-20 text-xs text-slate-500">{{ risk.category }}</div>
                                <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                        class="h-full rounded-full transition-all"
                                        :class="getRiskBarColor(risk.score)"
                                        :style="{ width: (risk.score / 100 * 100) + '%' }"
                                    ></div>
                                </div>
                                <div class="w-8 text-xs font-semibold text-slate-700 text-right">{{ risk.score }}</div>
                            </div>
                        </div>
                        <div class="flex items-center gap-3 mt-3 pt-3 border-t border-gray-200">
                            <div class="w-20 text-xs font-semibold text-slate-700">TOTAL</div>
                            <div class="flex-1 h-2.5 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    class="h-full rounded-full bg-primary"
                                    :style="{ width: totalRiskScore + '%' }"
                                ></div>
                            </div>
                            <div class="w-8 text-sm font-bold text-primary text-right">{{ totalRiskScore }}</div>
                        </div>
                    </div>
                </div>

                <!-- Evidence Panel -->
                <div class="flex-1 bg-white border border-gray-200 rounded-lg shadow-sm flex flex-col overflow-hidden">
                    <!-- Evidence Tabs -->
                    <div class="flex border-b border-gray-200">
                        <button
                            v-for="tab in evidenceTabs"
                            :key="tab.id"
                            @click="activeEvidenceTab = tab.id"
                            :class="[
                                'flex-1 px-3 py-2.5 text-xs font-medium transition-colors',
                                activeEvidenceTab === tab.id
                                    ? 'text-primary border-b-2 border-primary bg-slate-50'
                                    : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
                            ]"
                        >
                            {{ tab.label }}
                        </button>
                    </div>

                    <!-- Evidence Content -->
                    <div class="flex-1 overflow-y-auto p-4">
                        <!-- Transactions Tab -->
                        <div v-if="activeEvidenceTab === 'transactions'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Summary</div>
                                <div class="grid grid-cols-4 gap-3 text-sm">
                                    <div>
                                        <div class="text-slate-500">Total In (30d)</div>
                                        <div class="font-semibold text-slate-900">${{ transactionSummary.total_in.toLocaleString() }}</div>
                                    </div>
                                    <div>
                                        <div class="text-slate-500">Total Out (30d)</div>
                                        <div class="font-semibold text-slate-900">${{ transactionSummary.total_out.toLocaleString() }}</div>
                                    </div>
                                    <div>
                                        <div class="text-slate-500">Declared Income</div>
                                        <div class="font-semibold text-slate-900">${{ transactionSummary.declared_income.toLocaleString() }}/mo</div>
                                    </div>
                                    <div>
                                        <div class="text-slate-500">Income Ratio</div>
                                        <div class="font-semibold text-risk-critical">{{ transactionSummary.income_ratio }}%</div>
                                    </div>
                                </div>
                            </div>

                            <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Details</div>
                            <div class="space-y-2">
                                <div
                                    v-for="txn in transactions"
                                    :key="txn.id"
                                    @click="askAboutEvidence('transaction', txn)"
                                    class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg cursor-pointer transition-all hover:border-primary hover:bg-primary/5 hover:shadow-sm group"
                                    title="Ask SENTINEL about this transaction"
                                >
                                    <div class="flex items-center gap-4">
                                        <div class="text-xs text-slate-400 w-16">{{ txn.date }}</div>
                                        <div class="text-sm font-semibold min-w-[80px]" :class="txn.type === 'deposit' ? 'text-green-600' : 'text-slate-900'">
                                            {{ txn.type === 'deposit' ? '+' : '-' }}${{ txn.amount.toLocaleString() }}
                                        </div>
                                        <div class="text-xs text-slate-500">{{ txn.channel }}</div>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <span v-if="txn.flagged" class="w-5 h-5 flex items-center justify-center rounded-full bg-risk-critical/10 text-risk-critical text-xs font-bold">!</span>
                                        <svg class="w-4 h-4 text-slate-300 group-hover:text-primary transition-colors" viewBox="0 0 16 16" fill="none">
                                            <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Logins Tab -->
                        <div v-if="activeEvidenceTab === 'logins'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Summary</div>
                                <div class="grid grid-cols-4 gap-3 text-sm">
                                    <div>
                                        <div class="text-slate-500">Total Logins</div>
                                        <div class="font-semibold text-slate-900">{{ loginSummary.total }}</div>
                                    </div>
                                    <div>
                                        <div class="text-slate-500">Unique IPs</div>
                                        <div class="font-semibold text-slate-900">{{ loginSummary.unique_ips }}</div>
                                    </div>
                                    <div>
                                        <div class="text-slate-500">VPN Detected</div>
                                        <div class="font-semibold text-risk-critical">{{ loginSummary.vpn_count }}</div>
                                    </div>
                                    <div>
                                        <div class="text-slate-500">Countries</div>
                                        <div class="font-semibold" :class="loginSummary.countries > 2 ? 'text-risk-critical' : 'text-slate-900'">{{ loginSummary.countries }}</div>
                                    </div>
                                </div>
                            </div>

                            <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Details</div>
                            <div class="space-y-2">
                                <div
                                    v-for="login in logins"
                                    :key="login.id"
                                    @click="askAboutEvidence('login', login)"
                                    class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg cursor-pointer transition-all hover:border-primary hover:bg-primary/5 hover:shadow-sm group"
                                    title="Ask SENTINEL about this login"
                                >
                                    <div class="flex items-center gap-4">
                                        <div class="text-xs text-slate-400 w-24">{{ login.timestamp }}</div>
                                        <div class="text-sm font-medium text-slate-900">{{ login.country }}</div>
                                        <span v-if="login.vpn" class="px-1.5 py-0.5 text-xs font-medium bg-risk-critical/10 text-risk-critical rounded">VPN</span>
                                    </div>
                                    <svg class="w-4 h-4 text-slate-300 group-hover:text-primary transition-colors" viewBox="0 0 16 16" fill="none">
                                        <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                    </svg>
                                </div>
                            </div>
                        </div>

                        <!-- Network Tab -->
                        <div v-if="activeEvidenceTab === 'network'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Summary</div>
                                <div class="space-y-2 text-sm">
                                    <div class="flex items-center gap-2 text-risk-critical">
                                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                                            <path d="M7 1L13 12H1L7 1Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                                            <path d="M7 5V7.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                                            <circle cx="7" cy="10" r="0.5" fill="currentColor"/>
                                        </svg>
                                        {{ networkSummary.shared_devices }} accounts share device
                                    </div>
                                    <div class="flex items-center gap-2 text-risk-high">
                                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                                            <path d="M7 1L13 12H1L7 1Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                                            <path d="M7 5V7.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                                            <circle cx="7" cy="10" r="0.5" fill="currentColor"/>
                                        </svg>
                                        {{ networkSummary.flagged_connections }} flagged accounts in network
                                    </div>
                                    <div class="text-slate-600">
                                        Fraud ring probability: <span class="font-semibold" :class="networkSummary.fraud_ring_probability === 'HIGH' ? 'text-risk-critical' : networkSummary.fraud_ring_probability === 'MEDIUM' ? 'text-risk-high' : 'text-risk-low'">{{ networkSummary.fraud_ring_probability }}</span>
                                    </div>
                                </div>
                            </div>

                            <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">Network Graph</div>
                            <div class="bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg border border-gray-200 mb-4 overflow-hidden">
                                <!-- Dynamic Network Graph -->
                                <div v-if="networkConnections.length > 0" class="flex justify-center items-center py-8 px-4">
                                    <svg
                                        :width="networkGraphSize.width"
                                        :height="networkGraphSize.height"
                                        :viewBox="`-80 -80 ${networkGraphSize.width + 160} ${networkGraphSize.height + 160}`"
                                        class="overflow-visible"
                                    >
                                        <!-- Background glow for center -->
                                        <circle
                                            :cx="networkGraphSize.centerX"
                                            :cy="networkGraphSize.centerY"
                                            r="60"
                                            fill="url(#centerGlow)"
                                        />

                                        <!-- Gradient definitions -->
                                        <defs>
                                            <radialGradient id="centerGlow">
                                                <stop offset="0%" stop-color="#0ea5e9" stop-opacity="0.2"/>
                                                <stop offset="100%" stop-color="#0ea5e9" stop-opacity="0"/>
                                            </radialGradient>
                                            <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                                                <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.15"/>
                                            </filter>
                                        </defs>

                                        <!-- Edges (lines connecting nodes) -->
                                        <line
                                            v-for="(conn, idx) in networkConnections"
                                            :key="'edge-' + idx"
                                            :x1="networkGraphSize.centerX"
                                            :y1="networkGraphSize.centerY"
                                            :x2="getNodePosition(idx, networkConnections.length).x"
                                            :y2="getNodePosition(idx, networkConnections.length).y"
                                            :stroke="conn.flagged ? '#ef4444' : '#cbd5e1'"
                                            :stroke-width="conn.flagged ? 3 : 2"
                                            :stroke-dasharray="conn.flagged ? '0' : '6,4'"
                                            stroke-linecap="round"
                                        />

                                        <!-- Center Node (Current Case) -->
                                        <g :transform="`translate(${networkGraphSize.centerX}, ${networkGraphSize.centerY})`" filter="url(#shadow)">
                                            <circle r="44" fill="url(#centerNodeGradient)"/>
                                            <defs>
                                                <linearGradient id="centerNodeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                                    <stop offset="0%" stop-color="#38bdf8"/>
                                                    <stop offset="100%" stop-color="#0284c7"/>
                                                </linearGradient>
                                            </defs>
                                            <text y="6" text-anchor="middle" fill="white" font-size="16" font-weight="700">CASE</text>
                                        </g>

                                        <!-- Connected Nodes -->
                                        <g
                                            v-for="(conn, idx) in networkConnections"
                                            :key="'node-' + idx"
                                            :transform="`translate(${getNodePosition(idx, networkConnections.length).x}, ${getNodePosition(idx, networkConnections.length).y})`"
                                            class="cursor-pointer hover:opacity-80 transition-opacity"
                                            @click="askAboutEvidence('network', conn)"
                                            filter="url(#shadow)"
                                        >
                                            <!-- Node circle -->
                                            <circle
                                                r="44"
                                                :fill="conn.flagged ? '#fef2f2' : 'white'"
                                                :stroke="conn.flagged ? '#ef4444' : '#94a3b8'"
                                                :stroke-width="conn.flagged ? 3 : 2"
                                            />
                                            <!-- Account ID -->
                                            <text y="-4" text-anchor="middle" :fill="conn.flagged ? '#dc2626' : '#1e293b'" font-size="11" font-weight="600">
                                                {{ truncateAccountId(conn.account_id) }}
                                            </text>
                                            <!-- Connection type -->
                                            <text y="12" text-anchor="middle" fill="#64748b" font-size="10">
                                                {{ truncateConnectionType(conn.connection_type) }}
                                            </text>
                                            <!-- Flagged indicator -->
                                            <g v-if="conn.flagged" transform="translate(30, -30)">
                                                <circle r="12" fill="#ef4444"/>
                                                <text y="4" text-anchor="middle" fill="white" font-size="14" font-weight="bold">!</text>
                                            </g>
                                        </g>
                                    </svg>
                                </div>
                                <!-- No connections state -->
                                <div v-else class="flex items-center justify-center py-12">
                                    <div class="text-center text-slate-400 text-sm">
                                        <svg width="56" height="56" viewBox="0 0 56 56" fill="none" class="mx-auto mb-3 text-slate-300">
                                            <circle cx="28" cy="28" r="20" stroke="currentColor" stroke-width="2" stroke-dasharray="4,4"/>
                                            <circle cx="28" cy="28" r="8" fill="currentColor" opacity="0.3"/>
                                        </svg>
                                        No network connections detected
                                    </div>
                                </div>
                            </div>

                            <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Connected Accounts</div>
                            <div class="space-y-2">
                                <div
                                    v-for="conn in networkConnections"
                                    :key="conn.account_id"
                                    @click="askAboutEvidence('network', conn)"
                                    class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg cursor-pointer transition-all hover:border-primary hover:bg-primary/5 hover:shadow-sm group"
                                    title="Ask SENTINEL about this connection"
                                >
                                    <div class="flex items-center gap-4">
                                        <span class="text-sm font-semibold text-slate-900">{{ conn.account_id }}</span>
                                        <span class="text-xs text-slate-500">{{ conn.connection_type }}</span>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <span v-if="conn.flagged" class="px-1.5 py-0.5 text-xs font-medium bg-risk-critical/10 text-risk-critical rounded">Flagged</span>
                                        <svg class="w-4 h-4 text-slate-300 group-hover:text-primary transition-colors" viewBox="0 0 16 16" fill="none">
                                            <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- KYC Tab -->
                        <div v-if="activeEvidenceTab === 'kyc'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Verification Status</div>
                                <div class="space-y-2 text-sm">
                                    <div class="flex items-center justify-between">
                                        <span class="text-slate-500">ID Verification</span>
                                        <span class="font-medium text-green-600">Verified</span>
                                    </div>
                                    <div class="flex items-center justify-between">
                                        <span class="text-slate-500">Face Match</span>
                                        <span class="font-medium text-slate-900">{{ kycData.face_match }}%</span>
                                    </div>
                                    <div class="flex items-center justify-between">
                                        <span class="text-slate-500">Document Flags</span>
                                        <span class="font-medium" :class="kycData.document_flags.length > 0 ? 'text-risk-high' : 'text-green-600'">
                                            {{ kycData.document_flags.length > 0 ? kycData.document_flags.length + ' issues' : 'None' }}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">Customer Details</div>
                            <div class="space-y-3 text-sm">
                                <div class="flex justify-between">
                                    <span class="text-slate-500">Full Name</span>
                                    <span class="font-medium text-slate-900">{{ kycData.full_name }}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-slate-500">Date of Birth</span>
                                    <span class="font-medium text-slate-900">{{ kycData.dob }}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-slate-500">Country</span>
                                    <span class="font-medium text-slate-900">{{ kycData.country }}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-slate-500">Declared Income</span>
                                    <span class="font-medium text-slate-900">${{ kycData.declared_income.toLocaleString() }}/mo</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-slate-500">PEP Status</span>
                                    <span class="font-medium" :class="kycData.pep ? 'text-risk-high' : 'text-green-600'">{{ kycData.pep ? 'Yes' : 'No' }}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-slate-500">Sanctions</span>
                                    <span class="font-medium" :class="kycData.sanctions ? 'text-risk-critical' : 'text-green-600'">{{ kycData.sanctions ? 'Hit' : 'Clear' }}</span>
                                </div>
                            </div>

                            <div v-if="kycData.document_flags.length > 0" class="mt-4">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">Document Flags</div>
                                <div class="space-y-1">
                                    <div
                                        v-for="flag in kycData.document_flags"
                                        :key="flag"
                                        class="flex items-center gap-2 p-2 bg-risk-high/10 rounded text-sm text-risk-high"
                                    >
                                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                                            <path d="M7 1L13 12H1L7 1Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                                            <path d="M7 5V7.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                                            <circle cx="7" cy="10" r="0.5" fill="currentColor"/>
                                        </svg>
                                        {{ flag }}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Timeline Tab -->
                        <div v-if="activeEvidenceTab === 'timeline'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Case Timeline</div>
                                <div class="text-sm text-slate-600">Chronological view of all events related to this case</div>
                            </div>

                            <div class="space-y-2">
                                <div
                                    v-for="event in timelineEvents"
                                    :key="event.id"
                                    @click="askAboutEvidence('timeline', event)"
                                    class="flex items-start gap-4 p-3 bg-white border border-gray-200 rounded-lg cursor-pointer transition-all hover:border-primary hover:bg-primary/5 hover:shadow-sm group"
                                    title="Ask SENTINEL about this event"
                                >
                                    <div class="text-xs text-slate-400 w-28 flex-shrink-0">{{ event.timestamp }}</div>
                                    <div class="flex-1">
                                        <div class="text-sm text-slate-900">{{ event.description }}</div>
                                        <div class="text-xs text-slate-500 mt-1">Source: {{ event.source }}</div>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <span
                                            v-if="event.flagged"
                                            class="px-1.5 py-0.5 text-xs font-medium bg-risk-critical/10 text-risk-critical rounded"
                                        >Flagged</span>
                                        <svg class="w-4 h-4 text-slate-300 group-hover:text-primary transition-colors" viewBox="0 0 16 16" fill="none">
                                            <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Related Cases Tab -->
                        <div v-if="activeEvidenceTab === 'related'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Related Cases</div>
                                <div class="text-sm text-slate-600">Cases linked through shared devices, IPs, or financial connections</div>
                            </div>

                            <div class="space-y-2">
                                <div
                                    v-for="related in caseData.related_cases"
                                    :key="related.case_id"
                                    @click="askAboutEvidence('related', related)"
                                    class="p-3 bg-white border border-gray-200 rounded-lg cursor-pointer transition-all hover:border-primary hover:bg-primary/5 hover:shadow-sm group"
                                    title="Ask SENTINEL about this related case"
                                >
                                    <div class="flex items-center justify-between mb-2">
                                        <div class="flex items-center gap-3">
                                            <span class="text-sm font-semibold text-primary">{{ related.case_id }}</span>
                                            <span :class="getRiskBadgeClass(related.score >= 85 ? 'critical' : related.score >= 70 ? 'high' : 'medium')" class="px-2 py-0.5 text-xs font-semibold rounded">
                                                {{ related.score }}
                                            </span>
                                            <span class="text-xs text-slate-500">{{ related.status }}</span>
                                        </div>
                                        <svg class="w-4 h-4 text-slate-300 group-hover:text-primary transition-colors" viewBox="0 0 16 16" fill="none">
                                            <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                    </div>
                                    <div class="text-sm text-slate-900 mb-1">{{ related.customer }}</div>
                                    <div class="flex items-center gap-2">
                                        <span class="px-1.5 py-0.5 text-xs font-medium bg-slate-100 text-slate-600 rounded">{{ related.relationship }}</span>
                                        <span class="text-xs text-slate-500">{{ related.relationship_detail }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- SENTINEL Panel (Right - Hidden by default) -->
            <aside
                v-show="sentinelVisible && !isLoading && !loadError"
                class="w-[400px] flex-shrink-0 bg-white border border-gray-200 rounded-lg shadow-sm flex flex-col overflow-hidden"
            >
                <!-- SENTINEL Header -->
                <div class="px-4 py-3 border-b border-gray-200 bg-slate-50">
                    <h2 class="text-sm font-semibold text-slate-900">SENTINEL</h2>
                    <p class="text-xs text-slate-500 mt-0.5">AI Investigation Assistant</p>
                </div>

                <!-- Chat Messages -->
                <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
                    <div
                        v-for="message in messages"
                        :key="message.id"
                        :class="[
                            'flex',
                            message.sender === 'user' ? 'justify-end' : 'justify-start'
                        ]"
                    >
                        <div
                            :class="[
                                'max-w-[90%] rounded-lg px-4 py-3',
                                message.sender === 'user'
                                    ? 'bg-primary text-white'
                                    : 'bg-slate-100 text-slate-900'
                            ]"
                        >
                            <div v-if="message.sender === 'bot'" class="text-xs font-semibold text-primary mb-1">SENTINEL</div>
                            <div class="text-sm whitespace-pre-wrap">{{ message.text }}</div>
                            <div
                                :class="[
                                    'text-xs mt-2',
                                    message.sender === 'user' ? 'text-white/60' : 'text-slate-400'
                                ]"
                            >
                                {{ message.timestamp }}
                            </div>
                        </div>
                    </div>

                    <!-- Typing Indicator -->
                    <div v-if="isTyping" class="flex justify-start">
                        <div class="bg-slate-100 rounded-lg px-4 py-3">
                            <div class="flex items-center gap-1">
                                <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                                <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                                <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Suggested Questions -->
                <div class="px-4 py-3 border-t border-gray-100 bg-slate-50/50">
                    <div class="flex flex-wrap gap-2">
                        <button
                            v-for="suggestion in suggestedQuestions"
                            :key="suggestion"
                            @click="sendMessage(suggestion)"
                            class="px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-gray-200 rounded-full hover:bg-slate-100 hover:border-gray-300 transition-colors"
                        >
                            {{ suggestion }}
                        </button>
                    </div>
                </div>

                <!-- Chat Input -->
                <div class="p-4 border-t border-gray-200 bg-white">
                    <div class="flex items-center gap-2">
                        <input
                            v-model="userInput"
                            @keyup.enter="sendMessage(userInput)"
                            type="text"
                            placeholder="Ask SENTINEL..."
                            class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                        />
                        <button
                            @click="sendMessage(userInput)"
                            :disabled="!userInput.trim()"
                            class="px-3 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-light disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <path d="M14 2L7 9M14 2L9.5 14L7 9M14 2L2 6.5L7 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </aside>
        </div>

        <!-- Notes Modal -->
        <div v-if="showNotesModal" class="fixed inset-0 z-50 flex items-center justify-center">
            <div class="absolute inset-0 bg-black/50" @click="showNotesModal = false"></div>
            <div class="relative bg-white rounded-lg shadow-xl w-full max-w-lg mx-4">
                <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200">
                    <h3 class="text-base font-semibold text-slate-900">Add Investigation Notes</h3>
                    <button @click="showNotesModal = false" class="p-1 text-slate-400 hover:text-slate-600">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M6 6L14 14M14 6L6 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
                <div class="p-4">
                    <textarea
                        v-model="noteText"
                        rows="5"
                        placeholder="Enter your investigation notes..."
                        class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"
                    ></textarea>
                </div>
                <div class="flex items-center justify-end gap-2 px-4 py-3 border-t border-gray-200 bg-slate-50 rounded-b-lg">
                    <button
                        @click="showNotesModal = false"
                        class="px-4 py-2 text-sm font-medium text-slate-700 border border-gray-200 rounded-md hover:bg-gray-50"
                    >
                        Cancel
                    </button>
                    <button
                        @click="saveNote"
                        class="px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary-light"
                    >
                        Save Note
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
const route = useRoute()
const caseId = computed(() => route.params.id)
const config = useRuntimeConfig()

// API composable
const { chatWithSentinel } = useApi()

// Conversation history for API context
const conversationHistory = ref([])

// Loading and error states
const isLoading = ref(true)
const loadError = ref(null)

// UI State
const sentinelVisible = ref(false)
const activeEvidenceTab = ref('transactions')
const showNotesModal = ref(false)
const noteText = ref('')
const userInput = ref('')
const isTyping = ref(false)
const chatContainer = ref(null)

// Evidence tabs
const evidenceTabs = [
    { id: 'transactions', label: 'Transactions' },
    { id: 'logins', label: 'Logins' },
    { id: 'network', label: 'Network' },
    { id: 'kyc', label: 'KYC' },
    { id: 'timeline', label: 'Timeline' },
    { id: 'related', label: 'Related Cases' }
]

// Suggested questions
const suggestedQuestions = ref([
    'Why was this flagged?',
    'Show network analysis',
    'Find similar cases',
    'What should I check next?'
])

// Data from API - initialized with defaults
const alerts = ref([])
const timelineEvents = ref([])

const caseData = ref({
    case_id: caseId.value || '',
    risk_level: 'medium',
    risk_score: 0,
    sla_remaining: '4h remaining',
    customer_name: '',
    account_id: '',
    status: 'Loading...',
    related_cases: []
})

const transactionSummary = ref({
    total_in: 0,
    total_out: 0,
    declared_income: 0,
    income_ratio: 0
})

const transactions = ref([])

const loginSummary = ref({
    total: 0,
    unique_ips: 0,
    vpn_count: 0,
    countries: 0
})

const logins = ref([])

const networkSummary = ref({
    shared_devices: 0,
    flagged_connections: 0,
    fraud_ring_probability: 'LOW'
})

const networkConnections = ref([])

const kycData = ref({
    full_name: '',
    dob: 'N/A',
    country: '',
    declared_income: 0,
    face_match: 0,
    pep: false,
    sanctions: false,
    document_flags: []
})

const riskBreakdown = ref([
    { category: 'Income', score: 0 },
    { category: 'Geographic', score: 0 },
    { category: 'Network', score: 0 },
    { category: 'Behavior', score: 0 }
])

// Network Graph computed properties and helpers
const networkGraphSize = computed(() => {
    const connectionCount = networkConnections.value.length
    // Larger graph for better visibility
    const baseSize = 400
    const sizePerConnection = 50
    const size = Math.max(baseSize, baseSize + (connectionCount - 3) * sizePerConnection)
    return {
        width: size,
        height: size,
        centerX: size / 2,
        centerY: size / 2,
        radius: size / 2 - 80 // Distance from center to connected nodes
    }
})

function getNodePosition(index, total) {
    const { centerX, centerY, radius } = networkGraphSize.value
    // Distribute nodes evenly in a circle around the center
    // Start from top (-90 degrees) and go clockwise
    const angleStep = (2 * Math.PI) / total
    const angle = -Math.PI / 2 + index * angleStep
    return {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
    }
}

function truncateAccountId(accountId) {
    if (!accountId) return ''
    // Show shortened version for long IDs
    if (accountId.length > 12) {
        return accountId.substring(0, 10) + '...'
    }
    return accountId
}

function truncateConnectionType(type) {
    if (!type) return ''
    // Shorten common connection types
    const shortNames = {
        'Shared Device': 'Device',
        'Shared Ip': 'IP',
        'Same Owner': 'Owner',
        'Fund Transfer': 'Transfer'
    }
    return shortNames[type] || type.substring(0, 10)
}

// Fetch case data from API
async function fetchCaseData() {
    isLoading.value = true
    loadError.value = null

    try {
        const apiBase = config.public.apiBase || 'http://localhost:8000'
        const response = await fetch(`${apiBase}/api/cases/${caseId.value}/full/`)

        if (!response.ok) {
            throw new Error(`Failed to load case: ${response.status} ${response.statusText}`)
        }

        const data = await response.json()

        // Map case header
        caseData.value = {
            case_id: data.case?.case_id || caseId.value,
            risk_level: data.case?.risk_level || 'medium',
            risk_score: data.case?.risk_score || 0,
            sla_remaining: '4h remaining',
            customer_name: data.case?.customer_name || 'Unknown',
            account_id: data.case?.account_id || '',
            status: data.case?.status || 'OPEN',
            fraud_type: data.case?.fraud_type || '',
            related_cases: data.related_cases || []
        }

        // Map alerts
        alerts.value = data.alerts || []

        // Map transactions
        transactionSummary.value = data.transactions?.summary || {
            total_in: 0,
            total_out: 0,
            declared_income: 0,
            income_ratio: 0
        }
        transactions.value = (data.transactions?.items || []).map((t, idx) => ({
            id: t.transaction_id || idx,
            date: formatDateShort(t.date || t.timestamp),
            amount: t.amount || 0,
            type: t.type || 'unknown',
            channel: t.channel || 'Unknown',
            flagged: t.flagged || false
        }))

        // Map logins
        loginSummary.value = data.logins?.summary || {
            total: 0,
            unique_ips: 0,
            vpn_count: 0,
            countries: 0
        }
        logins.value = (data.logins?.items || []).map((l, idx) => ({
            id: l.event_id || idx,
            timestamp: formatDateTimeShort(l.timestamp),
            country: l.country || 'Unknown',
            vpn: l.vpn || false,
            device: l.device || 'Unknown',
            success: l.success !== false
        }))

        // Map network
        networkSummary.value = data.network?.summary || {
            shared_devices: 0,
            flagged_connections: 0,
            fraud_ring_probability: 'LOW'
        }
        networkConnections.value = data.network?.connections || []

        // Map KYC
        kycData.value = {
            full_name: data.kyc?.full_name || 'Unknown',
            dob: data.kyc?.dob || 'N/A',
            country: data.kyc?.country || 'Unknown',
            declared_income: data.kyc?.declared_income || 0,
            face_match: data.kyc?.face_match || 0,
            pep: data.kyc?.pep || false,
            sanctions: data.kyc?.sanctions || false,
            document_flags: data.kyc?.document_flags || []
        }

        // Map timeline
        timelineEvents.value = (data.timeline || []).map((e, idx) => ({
            id: idx,
            timestamp: formatDateTimeShort(e.timestamp),
            description: e.description || '',
            source: e.source || 'unknown',
            flagged: e.flagged || false
        }))

        // Calculate risk breakdown from case score
        const totalScore = data.case?.risk_score || 0
        riskBreakdown.value = calculateRiskBreakdown(totalScore, data)

    } catch (error) {
        console.error('Error fetching case data:', error)
        loadError.value = error.message
    } finally {
        isLoading.value = false
    }
}

// Helper to format dates
function formatDateShort(dateStr) {
    if (!dateStr) return ''
    try {
        const date = new Date(dateStr)
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    } catch {
        return dateStr.substring(0, 10)
    }
}

function formatDateTimeShort(dateStr) {
    if (!dateStr) return ''
    try {
        const date = new Date(dateStr)
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
    } catch {
        return dateStr.substring(0, 16)
    }
}

// Calculate risk breakdown based on available data
function calculateRiskBreakdown(totalScore, data) {
    // Distribute score based on data indicators
    const hasHighIncomeRatio = (data.transactions?.summary?.income_ratio || 0) > 100
    const hasMultipleCountries = (data.logins?.summary?.countries || 0) > 1
    const hasNetworkFlags = (data.network?.summary?.flagged_connections || 0) > 0
    const hasVpnUsage = (data.logins?.summary?.vpn_count || 0) > 0

    // Weight factors
    let incomeScore = hasHighIncomeRatio ? Math.min(35, totalScore * 0.4) : Math.min(10, totalScore * 0.15)
    let geoScore = hasMultipleCountries ? Math.min(25, totalScore * 0.3) : Math.min(5, totalScore * 0.1)
    let networkScore = hasNetworkFlags ? Math.min(25, totalScore * 0.25) : Math.min(5, totalScore * 0.1)
    let behaviorScore = hasVpnUsage ? Math.min(15, totalScore * 0.2) : Math.min(5, totalScore * 0.1)

    return [
        { category: 'Income', score: Math.round(incomeScore) },
        { category: 'Geographic', score: Math.round(geoScore) },
        { category: 'Network', score: Math.round(networkScore) },
        { category: 'Behavior', score: Math.round(behaviorScore) }
    ]
}

// Fetch data on mount
onMounted(() => {
    fetchCaseData()
})

const totalRiskScore = computed(() => {
    return riskBreakdown.value.reduce((sum, item) => sum + item.score, 0)
})

const messages = ref([])

// Methods
function toggleSentinel() {
    sentinelVisible.value = !sentinelVisible.value
}

function getAlertSeverityClass(severity) {
    const classes = {
        critical: 'bg-risk-critical text-white',
        high: 'bg-risk-high text-white',
        medium: 'bg-risk-medium text-white',
        low: 'bg-risk-low text-white'
    }
    return classes[severity] || classes.medium
}

function getRiskBadgeClass(level) {
    const classes = {
        critical: 'bg-risk-critical text-white',
        high: 'bg-risk-high text-white',
        medium: 'bg-risk-medium text-white',
        low: 'bg-risk-low text-white'
    }
    return classes[level] || classes.medium
}

function getRiskBarColor(score) {
    if (score >= 30) return 'bg-risk-critical'
    if (score >= 20) return 'bg-risk-high'
    if (score >= 10) return 'bg-risk-medium'
    return 'bg-risk-low'
}

function formatTime(date) {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

function formatAlertTime(isoString) {
    const date = new Date(isoString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function askAboutEvidence(type, item) {
    // Show SENTINEL if hidden
    if (!sentinelVisible.value) {
        sentinelVisible.value = true
    }

    let question = ''
    if (type === 'transaction') {
        question = `Tell me about the $${item.amount.toLocaleString()} ${item.type} on ${item.date}`
    } else if (type === 'login') {
        question = `Explain the login from ${item.country} on ${item.timestamp}`
    } else if (type === 'network') {
        question = `Tell me about the connection to ${item.account_id} (${item.connection_type})`
    } else if (type === 'timeline') {
        question = `Tell me more about this event: ${item.description}`
    } else if (type === 'related') {
        question = `Tell me about the relationship with ${item.case_id} (${item.customer}) - ${item.relationship}`
    }

    // Small delay to allow panel to open
    setTimeout(() => {
        sendMessage(question)
    }, 100)
}

function cleanResponseText(text) {
    // Remove "Suggested Follow-up Questions" section and everything after
    let cleaned = text
        .replace(/---\s*\n?\*?\*?Suggested Follow-up Questions:?\*?\*?[\s\S]*$/i, '')
        .replace(/\*\*Suggested Follow-up Questions:?\*\*[\s\S]*$/i, '')
        .replace(/Suggested Follow-up Questions:[\s\S]*$/i, '')

    // Strip markdown formatting
    cleaned = cleaned
        .replace(/\*\*([^*]+)\*\*/g, '$1')  // **bold** -> bold
        .replace(/\*([^*]+)\*/g, '$1')       // *italic* -> italic
        .replace(/^---+\s*$/gm, '')          // horizontal rules
        .replace(/^#+\s*/gm, '')             // headers
        .replace(/^\s*[-*]\s+/gm, '- ')      // normalize list items
        .replace(/^\d+\.\s+/gm, '')          // numbered lists
        .trim()

    return cleaned
}

async function sendMessage(text) {
    if (!text || !text.trim()) return

    const userMessage = text.trim()

    // Add user message
    messages.value.push({
        id: Date.now(),
        sender: 'user',
        text: userMessage,
        timestamp: formatTime(new Date())
    })

    userInput.value = ''
    isTyping.value = true

    // Scroll to bottom
    nextTick(() => {
        if (chatContainer.value) {
            chatContainer.value.scrollTop = chatContainer.value.scrollHeight
        }
    })

    try {
        // Call the real API
        const response = await chatWithSentinel(caseId.value, userMessage, conversationHistory.value)

        isTyping.value = false

        // Clean the response text
        const cleanedResponse = cleanResponseText(response.response)

        // Add bot response
        messages.value.push({
            id: Date.now(),
            sender: 'bot',
            text: cleanedResponse,
            timestamp: formatTime(new Date())
        })

        // Update conversation history for context (keep original for API)
        conversationHistory.value.push(
            { role: 'user', content: userMessage },
            { role: 'assistant', content: response.response }
        )

        // Update suggested questions if provided
        if (response.suggested_questions && response.suggested_questions.length > 0) {
            suggestedQuestions.value = response.suggested_questions
        }

    } catch (error) {
        isTyping.value = false
        console.error('Chat API error:', error)

        // Show error message to user
        messages.value.push({
            id: Date.now(),
            sender: 'bot',
            text: `Sorry, I encountered an error: ${error.message}. Please try again.`,
            timestamp: formatTime(new Date())
        })
    }

    nextTick(() => {
        if (chatContainer.value) {
            chatContainer.value.scrollTop = chatContainer.value.scrollHeight
        }
    })
}

function saveNote() {
    if (noteText.value.trim()) {
        console.log('Saving note:', noteText.value)
        noteText.value = ''
        showNotesModal.value = false
    }
}
</script>

<style scoped>
@keyframes bounce {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-4px);
    }
}

.animate-bounce {
    animation: bounce 0.6s infinite;
}
</style>
