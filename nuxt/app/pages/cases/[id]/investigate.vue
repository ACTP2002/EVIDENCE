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
            <!-- Investigation Panel (Left - Full width when SENTINEL hidden) -->
            <div class="flex-1 flex flex-col gap-4 overflow-hidden">
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
                                        Fraud ring probability: <span class="font-semibold text-risk-critical">HIGH</span>
                                    </div>
                                </div>
                            </div>

                            <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">Network Graph</div>
                            <div class="p-4 bg-slate-100 rounded-lg border border-gray-200 min-h-[120px] flex items-center justify-center mb-4">
                                <div class="text-center text-slate-500 text-sm">
                                    <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="mx-auto mb-2 text-slate-300">
                                        <circle cx="24" cy="12" r="6" stroke="currentColor" stroke-width="2"/>
                                        <circle cx="12" cy="36" r="6" stroke="currentColor" stroke-width="2"/>
                                        <circle cx="36" cy="36" r="6" stroke="currentColor" stroke-width="2"/>
                                        <path d="M20 16L14 32M28 16L34 32M18 36H30" stroke="currentColor" stroke-width="2"/>
                                    </svg>
                                    Network visualization coming soon
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
                v-show="sentinelVisible"
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

// API composable
const { chatWithSentinel } = useApi()

// Conversation history for API context
const conversationHistory = ref([])

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

// Alerts data
const alerts = ref([
    {
        alert_id: 'ALT-9901',
        severity: 'critical',
        description: 'Withdrawals exceed 6x declared income',
        detector_source: 'ml_anomaly',
        triggered_at: '2025-05-14T08:00:00Z'
    },
    {
        alert_id: 'ALT-9902',
        severity: 'high',
        description: 'VPN login from high-risk jurisdiction (Cyprus)',
        detector_source: 'behavior_detector',
        triggered_at: '2025-05-14T08:00:00Z'
    },
    {
        alert_id: 'ALT-9903',
        severity: 'critical',
        description: 'Device fingerprint shared with 3 flagged accounts',
        detector_source: 'network_analyzer',
        triggered_at: '2025-05-13T14:30:00Z'
    },
    {
        alert_id: 'ALT-9904',
        severity: 'high',
        description: 'Crypto-to-bank layering pattern detected',
        detector_source: 'ml_anomaly',
        triggered_at: '2025-05-12T11:15:00Z'
    },
    {
        alert_id: 'ALT-9905',
        severity: 'medium',
        description: 'Unusual transaction velocity - 5 deposits in 48 hours',
        detector_source: 'rule_engine',
        triggered_at: '2025-05-12T09:00:00Z'
    },
    {
        alert_id: 'ALT-9906',
        severity: 'high',
        description: 'KYC document shows potential AI-generated face',
        detector_source: 'document_analyzer',
        triggered_at: '2025-05-10T16:45:00Z'
    }
])

// Timeline data
const timelineEvents = ref([
    { id: 1, timestamp: 'May 14 09:22', description: 'Alert triggered: deposit spike pattern', source: 'ml_anomaly', flagged: true },
    { id: 2, timestamp: 'May 14 09:15', description: 'Withdrawal: $5,000 to bank account', source: 'transaction', flagged: true },
    { id: 3, timestamp: 'May 14 08:00', description: 'Login from Cyprus via VPN', source: 'auth', flagged: true },
    { id: 4, timestamp: 'May 13 14:22', description: 'Withdrawal: $3,200 to bank account', source: 'transaction', flagged: false },
    { id: 5, timestamp: 'May 12 14:15', description: 'Login from Cyprus via VPN', source: 'auth', flagged: true },
    { id: 6, timestamp: 'May 12 11:08', description: 'Deposit: $8,500 from crypto wallet', source: 'transaction', flagged: true },
    { id: 7, timestamp: 'May 10 16:45', description: 'Deposit: $12,000 from crypto wallet', source: 'transaction', flagged: true },
    { id: 8, timestamp: 'May 10 10:00', description: 'Login from USA, no VPN', source: 'auth', flagged: false },
    { id: 9, timestamp: 'May 08 09:30', description: 'Deposit: $1,200 via card', source: 'transaction', flagged: false }
])

// Hardcoded placeholder data
const caseData = ref({
    case_id: caseId.value || 'CASE-2025-88412',
    risk_level: 'critical',
    risk_score: 87,
    sla_remaining: '4h remaining',
    customer_name: 'James Miller',
    account_id: 'ACC-882193',
    status: 'Investigating',
    related_cases: [
        { case_id: 'CASE-2025-0812', score: 92, status: 'Investigating', customer: 'Sarah Chen', relationship: 'Shared Device', relationship_detail: 'Same device fingerprint DEV-IPHONE-99' },
        { case_id: 'CASE-2025-0799', score: 87, status: 'Pending Review', customer: 'Mike Johnson', relationship: 'Shared IP', relationship_detail: 'Multiple logins from IP 185.234.xx.xx' },
        { case_id: 'CASE-2025-0756', score: 78, status: 'Confirmed Fraud', customer: 'Alex Wong', relationship: 'Fund Transfer', relationship_detail: 'Direct transfers totaling $15,000' }
    ]
})

const transactionSummary = ref({
    total_in: 21700,
    total_out: 8200,
    declared_income: 4000,
    income_ratio: 542
})

const transactions = ref([
    { id: 1, date: 'May 14', amount: 5000, type: 'withdrawal', channel: 'Bank Transfer', flagged: true },
    { id: 2, date: 'May 13', amount: 3200, type: 'withdrawal', channel: 'Bank Transfer', flagged: false },
    { id: 3, date: 'May 12', amount: 8500, type: 'deposit', channel: 'Crypto', flagged: true },
    { id: 4, date: 'May 10', amount: 12000, type: 'deposit', channel: 'Crypto', flagged: true },
    { id: 5, date: 'May 08', amount: 1200, type: 'deposit', channel: 'Card', flagged: false }
])

const loginSummary = ref({
    total: 47,
    unique_ips: 12,
    vpn_count: 8,
    countries: 3
})

const logins = ref([
    { id: 1, timestamp: 'May 14 08:00', country: 'Cyprus', vpn: true, device: 'Chrome' },
    { id: 2, timestamp: 'May 13 09:20', country: 'USA', vpn: false, device: 'Chrome' },
    { id: 3, timestamp: 'May 12 14:15', country: 'Cyprus', vpn: true, device: 'Mobile' },
    { id: 4, timestamp: 'May 10 10:00', country: 'USA', vpn: false, device: 'Chrome' },
    { id: 5, timestamp: 'May 09 16:30', country: 'Russia', vpn: true, device: 'Firefox' }
])

const networkSummary = ref({
    shared_devices: 4,
    flagged_connections: 2
})

const networkConnections = ref([
    { account_id: 'ACC-0012', connection_type: 'Shared Device', flagged: true },
    { account_id: 'ACC-0034', connection_type: 'Shared IP', flagged: false },
    { account_id: 'ACC-0091', connection_type: 'Shared Device', flagged: true }
])

const kycData = ref({
    full_name: 'James Terrence Miller',
    dob: '1985-11-12',
    country: 'USA',
    declared_income: 4000,
    face_match: 94,
    pep: false,
    sanctions: false,
    document_flags: ['AI-generated face risk', 'Unusual font spacing']
})

const riskBreakdown = ref([
    { category: 'Income', score: 35 },
    { category: 'Geographic', score: 25 },
    { category: 'Network', score: 20 },
    { category: 'Behavior', score: 7 }
])

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
