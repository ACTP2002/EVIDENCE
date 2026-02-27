<template>
    <div class="flex flex-col min-h-screen bg-slate-50 overflow-x-hidden">
        <!-- Loading State -->
        <div v-if="loading" class="flex items-center justify-center min-h-screen">
            <div class="text-center">
                <div class="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p class="text-slate-500">Loading case data...</p>
            </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="flex items-center justify-center min-h-screen">
            <div class="text-center p-8 bg-white rounded-lg shadow-lg max-w-md">
                <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-risk-critical" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                </div>
                <h3 class="text-lg font-semibold text-slate-900 mb-2">Failed to Load Case</h3>
                <p class="text-slate-500 mb-4">{{ error }}</p>
                <button @click="$router.go(0)" class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-light">
                    Retry
                </button>
            </div>
        </div>

        <!-- Main Content (when loaded) -->
        <template v-else>
        <!-- Primary Header -->
        <header class="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200">
            <div class="flex items-center gap-4">
                <NuxtLink to="/cases" class="flex items-center gap-1 text-slate-500 hover:text-slate-700 text-sm">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
                            stroke-linejoin="round" />
                    </svg>
                    Cases
                </NuxtLink>
                <div class="h-4 w-px bg-gray-200"></div>
                <h1 class="text-base font-semibold text-slate-900">{{ caseData.case_id }}</h1>
                <span :class="getRiskBadgeClass(caseData.risk_level)" class="px-2 py-0.5 text-xs font-semibold rounded">
                    {{ caseData.risk_level.toUpperCase() }} ({{ caseData.risk_score }})
                </span>
            </div>
            <div class="flex items-center gap-1.5 text-sm text-slate-500">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5" />
                    <path d="M8 5V8L10 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                </svg>
                SLA: {{ caseData.sla_remaining }}
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
                <NuxtLink :to="`/cases/${caseId}/report`"
                    class="px-3 py-1.5 text-sm font-medium text-white bg-slate-900 rounded-md hover:bg-slate-800">
                    Generate Report
                </NuxtLink>
                <button @click="openCommentModal('fraud')" class="px-3 py-1.5 text-sm font-medium text-white bg-risk-critical rounded-md hover:bg-red-700">
                    Confirm Fraud
                </button>
                <button @click="openCommentModal('false_positive')"
                    class="px-3 py-1.5 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700">
                    False Positive
                </button>
            </div>
        </div>

        <!-- Main Content -->
        <div class="flex flex-1 p-4 gap-4 min-w-0">
            <!-- Investigation Panel (Left - Full width when AI SENTINEL hidden) -->
            <div class="flex-1 flex flex-col gap-4 min-w-0">
                <!-- Top Section: Alerts and Risk Breakdown -->
                <div class="flex gap-4 min-w-0">
                    <!-- Alerts Section -->
                    <div class="flex-1 min-w-0 bg-white border border-gray-200 rounded-lg shadow-sm p-4 flex flex-col">
                        <!-- Alerts Header with Expand/Collapse All -->
                        <div class="flex items-center justify-between mb-3">
                            <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                                Alerts ({{ alerts.length }})
                            </div>
                            <div class="flex items-center gap-2">
                                <button
                                    @click="expandAllAlerts"
                                    class="px-2 py-1 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded transition-colors">
                                    Expand All
                                </button>
                                <button
                                    @click="collapseAllAlerts"
                                    class="px-2 py-1 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded transition-colors">
                                    Collapse All
                                </button>
                            </div>
                        </div>
                        <!-- Alert Cards (no scroll, page scrolls naturally) -->
                        <div class="space-y-2">
                            <div v-for="alert in alerts" :key="alert.alert_id"
                                class="border border-gray-200 rounded-lg overflow-hidden">
                                <!-- Alert Summary (always visible) -->
                                <div
                                    @click="toggleAlert(alert.alert_id)"
                                    class="flex items-center justify-between p-3 cursor-pointer hover:bg-slate-50 transition-colors">
                                    <div class="flex items-center gap-2 flex-1 min-w-0">
                                        <span :class="getAlertSeverityClass(alert.severity)"
                                            class="px-2 py-0.5 text-xs font-semibold rounded flex-shrink-0">
                                            {{ alert.severity.toUpperCase() }}
                                        </span>
                                        <span class="text-xs text-slate-500 flex-shrink-0">{{ alert.alert_id }}</span>
                                        <span class="text-sm text-slate-900 truncate">{{ alert.description }}</span>
                                    </div>
                                    <!-- Maximize/Minimize Icon -->
                                    <button class="flex-shrink-0 w-6 h-6 flex items-center justify-center text-slate-400 hover:text-slate-600 transition-colors">
                                        <svg v-if="!expandedAlerts.has(alert.alert_id)" width="16" height="16" viewBox="0 0 16 16" fill="none">
                                            <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                        <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none">
                                            <path d="M4 10L8 6L12 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                    </button>
                                </div>
                                <!-- Alert Details (expanded) -->
                                <div v-if="expandedAlerts.has(alert.alert_id)"
                                    class="px-3 pb-3 pt-0 border-t border-gray-100 bg-slate-50">
                                    <div class="space-y-2 pt-2">
                                        <div class="text-sm text-slate-900">{{ alert.description }}</div>
                                        <div class="flex items-center gap-4 text-xs text-slate-500">
                                            <span><span class="font-medium">Source:</span> {{ alert.detector_source }}</span>
                                            <span><span class="font-medium">Time:</span> {{ formatAlertTime(alert.triggered_at) }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Risk Breakdown - Doughnut Chart -->
                    <div class="w-[280px] shrink-0 bg-white border border-gray-200 rounded-lg shadow-sm p-4">
                        <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">Risk Breakdown
                        </div>
                        <ChartsRiskDoughnut
                            :data="riskBreakdown"
                            :case-score="caseData.risk_score"
                            @ask-about="handleChartAsk"
                        />
                    </div>
                </div>

                <!-- Evidence Panel -->
                <div class="bg-white border border-gray-200 rounded-lg shadow-sm flex flex-col min-w-0">
                    <!-- Evidence Tabs -->
                    <div class="flex border-b border-gray-200 overflow-x-auto">
                        <button v-for="tab in evidenceTabs" :key="tab.id" @click="activeEvidenceTab = tab.id" :class="[
                            'flex-1 px-2 py-2.5 text-xs font-medium transition-colors whitespace-nowrap min-w-0',
                            activeEvidenceTab === tab.id
                                ? 'text-primary border-b-2 border-primary bg-slate-50'
                                : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
                        ]">
                            {{ tab.label }}
                        </button>
                    </div>

                    <!-- Evidence Content -->
                    <div class="p-4">
                        <!-- ML Insights Tab -->
                        <div v-if="activeEvidenceTab === 'ml-insights'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="flex items-center justify-between mb-2">
                                    <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide">SHAP Feature Analysis</div>
                                    <span class="px-2 py-0.5 text-xs font-medium bg-indigo-100 text-indigo-700 rounded">Explainable AI</span>
                                </div>
                                <p class="text-xs text-slate-500">How each feature contributed to the ML anomaly score. Red = increased risk, Green = decreased risk.</p>
                            </div>
                            <ChartsShapWaterfall
                                :evidence="rawAlerts"
                                @ask-about="handleChartAsk"
                            />
                        </div>

                        <!-- Transactions Tab -->
                        <div v-if="activeEvidenceTab === 'transactions'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Summary
                                </div>
                                <div class="grid grid-cols-4 gap-3 text-sm">
                                    <div>
                                        <div class="text-slate-500">Total In (30d)</div>
                                        <div class="font-semibold text-slate-900">${{
                                            transactionSummary.total_in.toLocaleString() }}</div>
                                    </div>
                                    <div>
                                        <div class="text-slate-500">Total Out (30d)</div>
                                        <div class="font-semibold text-slate-900">${{
                                            transactionSummary.total_out.toLocaleString() }}</div>
                                    </div>
                                    <div>
                                        <div class="text-slate-500">Declared Income</div>
                                        <div class="font-semibold text-slate-900">${{
                                            transactionSummary.declared_income.toLocaleString() }}/mo</div>
                                    </div>
                                    <div>
                                        <div class="text-slate-500">Income Ratio</div>
                                        <div class="font-semibold text-risk-critical">{{ transactionSummary.income_ratio
                                            }}%</div>
                                    </div>
                                </div>
                            </div>

                            <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Details</div>
                            <div class="space-y-2">
                                <div v-for="txn in transactions" :key="txn.id"
                                    @click="askAboutEvidence('transaction', txn)"
                                    class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg cursor-pointer transition-all hover:border-primary hover:bg-primary/5 hover:shadow-sm group"
                                    title="Ask AI SENTINEL about this transaction">
                                    <div class="flex items-center gap-4">
                                        <div class="text-xs text-slate-400 w-16">{{ txn.date }}</div>
                                        <div class="text-sm font-semibold min-w-[80px]"
                                            :class="txn.type === 'deposit' ? 'text-green-600' : 'text-slate-900'">
                                            {{ txn.type === 'deposit' ? '+' : '-' }}${{ txn.amount.toLocaleString() }}
                                        </div>
                                        <div class="text-xs text-slate-500">{{ txn.channel }}</div>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <span v-if="txn.flagged"
                                            class="w-5 h-5 flex items-center justify-center rounded-full bg-risk-critical/10 text-risk-critical text-xs font-bold">!</span>
                                        <svg class="w-4 h-4 text-slate-300 group-hover:text-primary transition-colors"
                                            viewBox="0 0 16 16" fill="none">
                                            <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.5"
                                                stroke-linecap="round" stroke-linejoin="round" />
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Logins Tab -->
                        <div v-if="activeEvidenceTab === 'logins'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Summary
                                </div>
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
                                        <div class="font-semibold"
                                            :class="loginSummary.countries > 2 ? 'text-risk-critical' : 'text-slate-900'">
                                            {{ loginSummary.countries }}</div>
                                    </div>
                                </div>
                            </div>

                            <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Details</div>
                            <div class="space-y-2">
                                <div v-for="login in logins" :key="login.id" @click="askAboutEvidence('login', login)"
                                    class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg cursor-pointer transition-all hover:border-primary hover:bg-primary/5 hover:shadow-sm group"
                                    title="Ask AI SENTINEL about this login">
                                    <div class="flex items-center gap-4">
                                        <div class="text-xs text-slate-400 w-24">{{ login.timestamp }}</div>
                                        <div class="text-sm font-medium text-slate-900">{{ login.country }}</div>
                                        <span v-if="login.vpn"
                                            class="px-1.5 py-0.5 text-xs font-medium bg-risk-critical/10 text-risk-critical rounded">VPN</span>
                                    </div>
                                    <svg class="w-4 h-4 text-slate-300 group-hover:text-primary transition-colors"
                                        viewBox="0 0 16 16" fill="none">
                                        <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.5"
                                            stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>
                                </div>
                            </div>
                        </div>

                        <!-- Network Tab -->
                        <div v-if="activeEvidenceTab === 'network'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Summary
                                </div>
                                <div class="space-y-2 text-sm">
                                    <div class="flex items-center gap-2 text-risk-critical">
                                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                                            <path d="M7 1L13 12H1L7 1Z" stroke="currentColor" stroke-width="1.5"
                                                stroke-linejoin="round" />
                                            <path d="M7 5V7.5" stroke="currentColor" stroke-width="1.5"
                                                stroke-linecap="round" />
                                            <circle cx="7" cy="10" r="0.5" fill="currentColor" />
                                        </svg>
                                        {{ networkSummary.shared_devices }} accounts share IP
                                    </div>
                                    <div class="flex items-center gap-2 text-risk-high">
                                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                                            <path d="M7 1L13 12H1L7 1Z" stroke="currentColor" stroke-width="1.5"
                                                stroke-linejoin="round" />
                                            <path d="M7 5V7.5" stroke="currentColor" stroke-width="1.5"
                                                stroke-linecap="round" />
                                            <circle cx="7" cy="10" r="0.5" fill="currentColor" />
                                        </svg>
                                        {{ networkSummary.flagged_connections }} flagged accounts in network
                                    </div>
                                    <div class="text-slate-600">
                                        Fraud ring probability: <span
                                            class="font-semibold text-risk-critical">HIGH</span>
                                    </div>
                                </div>
                            </div>

                            <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">Network Graph
                            </div>
                            <ChartsNetworkGraph
                                :graph-data="networkGraphData"
                                :primary-user-id="caseData.customer_name"
                                @ask-about="handleChartAsk"
                                @fullscreen-change="onNetworkFullscreenChange"
                            />

                            <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Connected
                                Accounts</div>
                            <div class="space-y-2">
                                <div v-for="conn in networkConnections" :key="conn.account_id"
                                    @click="askAboutEvidence('network', conn)"
                                    class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg cursor-pointer transition-all hover:border-primary hover:bg-primary/5 hover:shadow-sm group"
                                    title="Ask AI SENTINEL about this connection">
                                    <div class="flex items-center gap-4">
                                        <span class="text-sm font-semibold text-slate-900">{{ conn.account_id }}</span>
                                        <span class="text-xs text-slate-500">{{ conn.connection_type }}</span>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <span v-if="conn.flagged"
                                            class="px-1.5 py-0.5 text-xs font-medium bg-risk-critical/10 text-risk-critical rounded">Flagged</span>
                                        <svg class="w-4 h-4 text-slate-300 group-hover:text-primary transition-colors"
                                            viewBox="0 0 16 16" fill="none">
                                            <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.5"
                                                stroke-linecap="round" stroke-linejoin="round" />
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Risk Profile Tab -->
                        <div v-if="activeEvidenceTab === 'risk-profile'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="flex items-center justify-between mb-2">
                                    <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide">Multi-Dimensional Risk Analysis</div>
                                    <span class="px-2 py-0.5 text-xs font-medium bg-red-100 text-red-700 rounded">vs Normal Baseline</span>
                                </div>
                                <p class="text-xs text-slate-500">Compares this case against normal user behavior across 6 risk dimensions.</p>
                            </div>
                            <ChartsRiskRadar
                                :status="rawStatus"
                                :profile="rawProfile"
                                :case-score="caseData.risk_score"
                                @ask-about="handleChartAsk"
                            />
                        </div>

                        <!-- Event Timeline Tab -->
                        <div v-if="activeEvidenceTab === 'event-timeline'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="flex items-center justify-between mb-2">
                                    <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide">Visual Event Timeline</div>
                                    <span class="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 rounded">Chronological</span>
                                </div>
                                <p class="text-xs text-slate-500">All case events plotted chronologically. Click any event to ask AI SENTINEL.</p>
                            </div>
                            <ChartsEventTimeline
                                :alerts="rawAlerts"
                                :transactions="rawTransactions"
                                :logins="rawLogins"
                                @ask-about="handleChartAsk"
                            />

                            <!-- Event List -->
                            <div class="mt-4 pt-4 border-t border-gray-200">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Event Details</div>
                                <div class="space-y-2">
                                    <div v-for="event in timelineEvents" :key="event.id"
                                        @click="askAboutEvidence('timeline', event)"
                                        class="flex items-start gap-4 p-3 bg-white border border-gray-200 rounded-lg cursor-pointer transition-all hover:border-primary hover:bg-primary/5 hover:shadow-sm group"
                                        title="Ask AI SENTINEL about this event">
                                        <div class="text-xs text-slate-400 w-28 flex-shrink-0">{{ event.timestamp }}</div>
                                        <div class="flex-1">
                                            <div class="text-sm text-slate-900">{{ event.description }}</div>
                                            <div class="text-xs text-slate-500 mt-1">Source: {{ event.source }}</div>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <span v-if="event.flagged"
                                                class="px-1.5 py-0.5 text-xs font-medium bg-risk-critical/10 text-risk-critical rounded">Flagged</span>
                                            <svg class="w-4 h-4 text-slate-300 group-hover:text-primary transition-colors"
                                                viewBox="0 0 16 16" fill="none">
                                                <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.5"
                                                    stroke-linecap="round" stroke-linejoin="round" />
                                            </svg>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- KYC Tab -->
                        <div v-if="activeEvidenceTab === 'kyc'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">
                                    Verification Status</div>
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
                                        <span class="font-medium"
                                            :class="kycData.document_flags.length > 0 ? 'text-risk-high' : 'text-green-600'">
                                            {{ kycData.document_flags.length > 0 ? kycData.document_flags.length +
                                                'issues' : 'None' }}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">Customer
                                Details</div>
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
                                    <span class="font-medium text-slate-900">${{
                                        kycData.declared_income.toLocaleString() }}/mo</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-slate-500">PEP Status</span>
                                    <span class="font-medium"
                                        :class="kycData.pep ? 'text-risk-high' : 'text-green-600'">{{ kycData.pep ?
                                            'Yes' : 'No' }}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-slate-500">Sanctions</span>
                                    <span class="font-medium"
                                        :class="kycData.sanctions ? 'text-risk-critical' : 'text-green-600'">{{
                                            kycData.sanctions ? 'Hit' : 'Clear' }}</span>
                                </div>
                            </div>

                            <div v-if="kycData.document_flags.length > 0" class="mt-4">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">Document
                                    Flags</div>
                                <div class="space-y-1">
                                    <div v-for="flag in kycData.document_flags" :key="flag"
                                        class="flex items-center gap-2 p-2 bg-risk-high/10 rounded text-sm text-risk-high">
                                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                                            <path d="M7 1L13 12H1L7 1Z" stroke="currentColor" stroke-width="1.5"
                                                stroke-linejoin="round" />
                                            <path d="M7 5V7.5" stroke="currentColor" stroke-width="1.5"
                                                stroke-linecap="round" />
                                            <circle cx="7" cy="10" r="0.5" fill="currentColor" />
                                        </svg>
                                        {{ flag }}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Related Cases Tab -->
                        <div v-if="activeEvidenceTab === 'related'">
                            <div class="p-4 bg-slate-50 rounded-lg border border-gray-200 mb-4">
                                <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">Related Cases</div>
                                <div class="text-sm text-slate-600">Cases linked through shared devices, IPs, trading patterns, or financial connections</div>
                            </div>

                            <!-- No Related Cases -->
                            <div v-if="relatedCases.length === 0" class="text-center py-8 text-slate-500">
                                <svg class="w-12 h-12 mx-auto mb-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                                </svg>
                                <p class="text-sm">No related cases found</p>
                            </div>

                            <!-- Related Cases List -->
                            <div v-else class="space-y-4">
                                <div v-for="related in relatedCases" :key="related.case_id"
                                    class="bg-white border border-gray-200 rounded-lg overflow-hidden">
                                    <!-- Case Header -->
                                    <div class="p-4 border-b border-gray-100">
                                        <div class="flex items-center justify-between mb-3">
                                            <div class="flex items-center gap-3">
                                                <span class="text-base font-semibold text-primary">{{ related.case_id }}</span>
                                                <span :class="getRiskBadgeClass(related.risk_level?.toLowerCase())"
                                                    class="px-2 py-0.5 text-xs font-semibold rounded">
                                                    {{ related.risk_level }} ({{ related.case_score }})
                                                </span>
                                                <span class="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 rounded">
                                                    {{ related.status }}
                                                </span>
                                                <span v-if="related.confusion_matrix"
                                                    :class="{
                                                        'bg-green-100 text-green-800': related.confusion_matrix === 'TP',
                                                        'bg-red-100 text-red-800': related.confusion_matrix === 'FP',
                                                        'bg-yellow-100 text-yellow-800': related.confusion_matrix === 'FN',
                                                        'bg-slate-100 text-slate-700': related.confusion_matrix === 'TN'
                                                    }"
                                                    class="px-2 py-0.5 text-xs font-medium rounded cursor-help"
                                                    :title="getConfusionMatrixDescription(related.confusion_matrix)">
                                                    {{ getConfusionMatrixLabel(related.confusion_matrix) }}
                                                </span>
                                            </div>
                                        </div>

                                        <!-- Similarity & Cluster Info -->
                                        <div class="flex items-center gap-4 text-sm">
                                            <div class="flex items-center gap-2">
                                                <span class="text-slate-500">Similarity:</span>
                                                <span class="font-semibold text-slate-900">{{ related.similarity_score }}%</span>
                                                <div class="w-20 h-2 bg-slate-200 rounded-full overflow-hidden">
                                                    <div class="h-full bg-primary rounded-full" :style="{ width: related.similarity_score + '%' }"></div>
                                                </div>
                                            </div>
                                            <div class="h-4 w-px bg-gray-200"></div>
                                            <div class="flex items-center gap-2">
                                                <span class="text-slate-500">Cluster:</span>
                                                <span class="px-2 py-0.5 text-xs font-medium bg-amber-100 text-amber-800 rounded">
                                                    {{ related.cluster_type }}
                                                </span>
                                            </div>
                                            <div class="h-4 w-px bg-gray-200"></div>
                                            <div class="flex items-center gap-2">
                                                <span class="text-slate-500">User:</span>
                                                <span class="font-medium text-slate-900">{{ related.user_id }}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Related Case Alerts -->
                                    <div class="p-4 bg-slate-50">
                                        <div class="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">
                                            Alerts in Related Case ({{ related.alerts?.length || 0 }})
                                        </div>
                                        <div class="space-y-2">
                                            <div v-for="alert in related.alerts" :key="alert.alert_id"
                                                @click="askAboutEvidence('related_alert', { ...alert, parent_case: related.case_id })"
                                                class="p-3 bg-white border border-gray-200 rounded-lg cursor-pointer hover:border-primary hover:shadow-sm transition-all group">
                                                <div class="flex items-center gap-2 mb-1">
                                                    <span :class="getAlertSeverityClass(alert.severity?.toLowerCase())"
                                                        class="px-2 py-0.5 text-xs font-semibold rounded">
                                                        {{ alert.severity }}
                                                    </span>
                                                    <span class="text-xs text-slate-500">{{ alert.alert_id }}</span>
                                                    <span class="text-sm font-medium text-slate-900">{{ alert.signal }}</span>
                                                </div>
                                                <div class="text-xs text-slate-600 line-clamp-2">{{ alert.evidence }}</div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Actions -->
                                    <div class="px-4 py-3 bg-white border-t border-gray-100 flex items-center justify-between">
                                        <span class="text-xs text-slate-500">
                                            Opened: {{ new Date(related.opened_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>

        <!-- AI SENTINEL Floating Button -->
        <button @click="toggleSentinel"
            class="fixed bottom-6 right-6 group inline-flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold text-white
                bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-500
                shadow-lg shadow-blue-500/25 ring-1 ring-white/10
                transition-all duration-300
                hover:shadow-xl hover:shadow-blue-500/30 hover:-translate-y-0.5
                active:translate-y-0 active:shadow-lg
                focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500"
            :class="{ 'scale-0 opacity-0': sentinelVisible, 'scale-100 opacity-100': !sentinelVisible, 'z-[10000]': networkGraphFullscreen, 'z-50': !networkGraphFullscreen }">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none">
                <path d="M12 2l1.2 4.3L17.5 7.5l-4.3 1.2L12 13l-1.2-4.3L6.5 7.5l4.3-1.2L12 2z" fill="currentColor" />
                <path d="M19 12l.8 2.7 2.7.8-2.7.8L19 19l-.8-2.7-2.7-.8 2.7-.8L19 12z" fill="currentColor" opacity=".9" />
            </svg>
            <span>AI SENTINEL</span>
        </button>

        <!-- AI SENTINEL Floating Panel -->
        <div v-show="sentinelVisible"
            class="fixed bottom-6 right-6 w-[400px] h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden"
            :class="{ 'z-[10000]': networkGraphFullscreen, 'z-50': !networkGraphFullscreen }">
            <!-- AI SENTINEL Header -->
            <div class="px-4 py-3 border-b border-gray-200 bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-500">
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-sm font-semibold text-white">AI SENTINEL</h2>
                        <p class="text-xs text-white/80 mt-0.5">AI Investigation Assistant</p>
                    </div>
                    <button @click="toggleSentinel"
                        class="w-8 h-8 rounded-full hover:bg-white/20 flex items-center justify-center transition-colors">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M15 5L5 15M5 5L15 15" stroke="white" stroke-width="2" stroke-linecap="round" />
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Chat Messages -->
            <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                <div v-for="message in messages" :key="message.id" :class="[
                    'flex',
                    message.sender === 'user' ? 'justify-end' : 'justify-start'
                ]">
                    <div :class="[
                        'max-w-[90%] rounded-2xl px-4 py-3',
                        message.sender === 'user'
                            ? 'bg-primary text-white rounded-br-sm'
                            : 'bg-white text-slate-900 shadow-sm rounded-bl-sm'
                    ]">
                        <div v-if="message.sender === 'bot'" class="text-xs font-semibold text-primary mb-1">
                            AI SENTINEL</div>
                        <div class="text-sm whitespace-pre-wrap">{{ message.text }}</div>
                        <div :class="[
                            'text-xs mt-2',
                            message.sender === 'user' ? 'text-white/60' : 'text-slate-400'
                        ]">
                            {{ message.timestamp }}
                        </div>
                    </div>
                </div>

                <!-- Typing Indicator -->
                <div v-if="isTyping" class="flex justify-start">
                    <div class="bg-white rounded-2xl px-4 py-3 shadow-sm">
                        <div class="flex items-center gap-1">
                            <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                            <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                                style="animation-delay: 0.1s"></div>
                            <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                                style="animation-delay: 0.2s"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Suggested Questions -->
            <div class="px-4 py-3 border-t border-gray-100 bg-white">
                <div class="text-xs text-slate-400 mb-2">Suggested:</div>
                <div class="flex flex-wrap gap-2">
                    <button v-for="suggestion in suggestedQuestions" :key="suggestion"
                        @click="sendMessage(suggestion)"
                        class="px-3 py-1.5 text-xs font-medium text-slate-600 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors">
                        {{ suggestion }}
                    </button>
                </div>
            </div>

            <!-- Chat Input -->
            <div class="p-4 border-t border-gray-200 bg-white">
                <div class="flex items-center gap-2">
                    <input v-model="userInput" @keyup.enter="sendMessage(userInput)" type="text"
                        placeholder="Ask AI SENTINEL..."
                        class="flex-1 px-4 py-2.5 border border-gray-200 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary" />
                    <button @click="sendMessage(userInput)" :disabled="!userInput.trim()"
                        class="w-10 h-10 bg-primary text-white rounded-full flex items-center justify-center hover:bg-primary-light disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M14 2L7 9M14 2L9.5 14L7 9M14 2L2 6.5L7 9" stroke="currentColor"
                                stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>

        <!-- Comment Confirmation Modal -->
        <div v-if="showCommentModal" class="fixed inset-0 z-50 flex items-center justify-center">
            <div class="absolute inset-0 bg-black/50" @click="closeCommentModal"></div>
            <div class="relative bg-white rounded-lg shadow-xl w-full max-w-lg mx-4">
                <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200">
                    <h3 class="text-base font-semibold text-slate-900">Comment</h3>
                    <button @click="closeCommentModal" class="p-1 text-slate-400 hover:text-slate-600">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M6 6L14 14M14 6L6 14" stroke="currentColor" stroke-width="1.5"
                                stroke-linecap="round" />
                        </svg>
                    </button>
                </div>
                <div class="p-4">
                    <div class="mb-3 p-3 rounded-lg" :class="decisionType === 'fraud' ? 'bg-red-50 text-risk-critical' : 'bg-green-50 text-green-700'">
                        <span class="font-medium">Decision:</span> {{ decisionType === 'fraud' ? 'Confirm Fraud' : 'False Positive' }}
                    </div>
                    <textarea v-model="commentText" rows="5" placeholder="Type any comment here"
                        class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"></textarea>
                </div>
                <div
                    class="flex items-center justify-end gap-2 px-4 py-3 border-t border-gray-200 bg-slate-50 rounded-b-lg">
                    <button @click="closeCommentModal"
                        class="px-4 py-2 text-sm font-medium text-slate-700 border border-gray-200 rounded-md hover:bg-gray-50">
                        Cancel
                    </button>
                    <button @click="submitDecision"
                        class="px-4 py-2 text-sm font-medium text-white rounded-md"
                        :class="decisionType === 'fraud' ? 'bg-risk-critical hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'">
                        Submit
                    </button>
                </div>
            </div>
        </div>
        </template>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'

const route = useRoute()
const caseId = computed(() => route.params.id)

// API composable
const { chatWithSentinel, getInvestigateData, getCaseNetworkGraph } = useApi()

// Loading state
const loading = ref(true)
const error = ref(null)

// Conversation history for API context
const conversationHistory = ref([])

// UI State
const sentinelVisible = ref(false)
const activeEvidenceTab = ref('ml-insights')
const showCommentModal = ref(false)
const commentText = ref('')
const decisionType = ref('') // 'fraud' or 'false_positive'
const userInput = ref('')
const isTyping = ref(false)
const chatContainer = ref(null)
const expandedAlerts = ref(new Set()) // Track which alerts are expanded (all collapsed by default)
const networkGraphFullscreen = ref(false)

// Evidence tabs - Network second, added Risk Profile and visual Timeline
const evidenceTabs = [
    { id: 'ml-insights', label: 'ML Insights' },
    { id: 'network', label: 'Network' },
    { id: 'risk-profile', label: 'Risk Profile' },
    { id: 'event-timeline', label: 'Timeline' },
    { id: 'transactions', label: 'Transactions' },
    { id: 'logins', label: 'Logins' },
    { id: 'kyc', label: 'KYC' },
    { id: 'related', label: 'Related Cases' }
]

// Suggested questions
const suggestedQuestions = ref([
    'Why was this flagged?',
    'Show network analysis',
    'Find similar cases',
    'What should I check next?'
])

// Data refs - will be populated from API
const alerts = ref([])
const rawAlerts = ref([]) // Raw alerts with SHAP evidence for waterfall chart
const timelineEvents = ref([])
const caseData = ref({
    case_id: '',
    risk_level: 'medium',
    risk_score: 0,
    sla_remaining: '4h remaining',
    customer_name: 'Loading...',
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
    flagged_connections: 0
})
const networkConnections = ref([])
const networkGraphData = ref({ nodes: [], edges: [] })
const kycData = ref({
    full_name: 'Loading...',
    dob: '',
    country: '',
    declared_income: 0,
    face_match: 0,
    pep: false,
    sanctions: false,
    document_flags: []
})
const riskBreakdown = ref([])
const relatedCases = ref([])

// Dummy related case data for CASE-20260207-0001
const RELATED_CASE_DATA = {
    case_id: "CASE-20250910-0002",
    user_id: "u_004",
    status: "Closed",
    opened_at: "2026-02-09T14:22:41Z",
    case_score: 92,
    risk_level: "HIGH",
    confusion_matrix: "TP",
    similarity_score: 88,
    cluster_type: "OPPOSITE TRADING",
    alerts: [
        {
            alert_id: "A-0101",
            signal: "Account Takeover Risk",
            severity: "HIGH",
            evidence: "5 consecutive failed login attempts from 4 distinct IP addresses across PH, TH, and RU. Automated brute-force attack suspected."
        },
        {
            alert_id: "A-0102",
            signal: "Sudden Withdrawal Spike",
            severity: "HIGH",
            evidence: "Large withdrawal of $75,000 detected within 15 minutes of suspicious login."
        },
        {
            alert_id: "A-0103",
            signal: "Monetary Deviation",
            severity: "MED",
            evidence: "Transaction amount significantly deviates from short-term trend (residual=3.42σ)."
        },
        {
            alert_id: "A-0104",
            signal: "Multi-Accounting",
            severity: "HIGH",
            evidence: "Device fingerprint linked to 5 other accounts previously flagged for bonus abuse."
        }
    ]
}

// Raw data refs for charts
const rawStatus = ref({})
const rawProfile = ref({})
const rawTransactions = ref([])
const rawLogins = ref([])

// ============ DATA TRANSFORMATION FUNCTIONS ============

function transformAlerts(caseAlerts) {
    if (!caseAlerts || !Array.isArray(caseAlerts)) return []
    return caseAlerts.map(alert => ({
        alert_id: alert.alert_id,
        severity: alert.severity?.toLowerCase() || 'medium',
        description: alert.evidence?.[0]?.explanation || alert.signal || 'Anomaly detected',
        detector_source: alert.detector_type?.toLowerCase().replace(/ /g, '_') || 'ml_anomaly',
        triggered_at: alert.event_time
    }))
}

function transformTransactions(txnList, statusData) {
    if (!txnList || !Array.isArray(txnList)) return []
    return txnList.map((txn, idx) => {
        const date = new Date(txn.event_time)
        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        const amount = txn.data?.amount || 0
        const eventType = txn.event_type?.toLowerCase() || 'unknown'
        // In trading: buy = money out (buying stock), sell = money in (selling stock)
        // deposit = money in, withdrawal = money out
        const isMoneyIn = eventType === 'sell' || eventType === 'deposit'
        const stockId = txn.data?.stock_id || ''

        return {
            id: idx + 1,
            date: dateStr,
            amount: Math.abs(amount),
            type: isMoneyIn ? 'deposit' : 'withdrawal',
            eventType: eventType, // Keep original event type for display
            channel: stockId ? `${eventType.toUpperCase()} ${stockId}` : (txn.data?.channel || 'Unknown'),
            flagged: amount > 10000 // Flag high-value transactions
        }
    }).sort((a, b) => b.id - a.id).slice(0, 20)
}

function transformLogins(loginList, networkList) {
    if (!loginList || !Array.isArray(loginList)) return []

    // Build VPN lookup from network events
    const vpnSessions = new Set()
    if (networkList && Array.isArray(networkList)) {
        networkList.forEach(n => {
            if (n.data?.vpn_suspected) {
                vpnSessions.add(n.session_id)
            }
        })
    }

    return loginList.map((login, idx) => {
        const date = new Date(login.event_time)
        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
        const country = login.data?.geo?.country || 'Unknown'
        const isVpn = vpnSessions.has(login.session_id)

        return {
            id: idx + 1,
            timestamp: dateStr,
            country: country,
            vpn: isVpn,
            device: login.data?.user_agent?.split('/')[0] || 'Browser'
        }
    }).slice(0, 20)
}

function computeLoginSummary(loginList, networkList) {
    if (!loginList || !Array.isArray(loginList)) {
        return { total: 0, unique_ips: 0, vpn_count: 0, countries: 0 }
    }

    const uniqueIps = new Set(loginList.map(l => l.ip).filter(Boolean))
    const countries = new Set(loginList.map(l => l.data?.geo?.country).filter(Boolean))

    let vpnCount = 0
    if (networkList && Array.isArray(networkList)) {
        vpnCount = networkList.filter(n => n.data?.vpn_suspected).length
    }

    return {
        total: loginList.length,
        unique_ips: uniqueIps.size,
        vpn_count: vpnCount,
        countries: countries.size
    }
}

function transformNetworkConnections(networkList) {
    if (!networkList || !Array.isArray(networkList)) return []

    // Extract unique devices/IPs as connections
    const connections = []
    const seen = new Set()

    networkList.forEach(n => {
        const key = n.device_id || n.ip
        if (key && !seen.has(key)) {
            seen.add(key)
            connections.push({
                account_id: n.device_id || n.ip,
                connection_type: n.data?.vpn_suspected ? 'VPN Connection' : 'Shared IP',
                flagged: n.data?.vpn_suspected || false
            })
        }
    })

    return connections.slice(0, 10)
}

function computeNetworkSummary(networkList) {
    if (!networkList || !Array.isArray(networkList)) {
        return { shared_devices: 0, flagged_connections: 0 }
    }

    // Check for shared IP accounts (fraud ring indicator)
    const sharedIpAccounts = networkList.reduce((max, n) => {
        const count = n.data?.shared_ip_accounts || 0
        return count > max ? count : max
    }, 0)

    // Count flagged connections (VPN, proxy, or explicitly flagged)
    const flaggedCount = networkList.filter(n =>
        n.data?.vpn_suspected ||
        n.data?.proxy_detected ||
        n.data?.flagged ||
        n.data?.tor_exit_node
    ).length

    return {
        shared_devices: sharedIpAccounts,
        flagged_connections: flaggedCount
    }
}

function computeNetworkSummaryFromGraph(graphData, networkList) {
    if (!graphData || !graphData.nodes) {
        return computeNetworkSummary(networkList)
    }

    // Count user nodes (accounts in the network)
    const userNodes = graphData.nodes.filter(n => n.type === 'user')
    const sharedAccounts = userNodes.length

    // Count IP nodes with high connection counts or flagged
    const ipNodes = graphData.nodes.filter(n => n.type === 'ip')
    const suspiciousIps = ipNodes.filter(n =>
        (n.data?.connection_count || 0) > 2 ||
        n.data?.vpn_suspected
    ).length

    // Count flagged user accounts (accounts other than the primary that are connected)
    // In a fraud ring, accounts sharing the same IP are suspicious
    const flaggedAccounts = sharedAccounts > 2 ? sharedAccounts - 1 : 0

    return {
        shared_devices: sharedAccounts,
        flagged_connections: flaggedAccounts
    }
}

function transformKycData(profile) {
    if (!profile) {
        return {
            full_name: 'Not Available',
            dob: '',
            country: '',
            declared_income: 0,
            face_match: 0,
            pep: false,
            sanctions: false,
            document_flags: []
        }
    }

    const kyc = profile.kyc || {}
    const risk = profile.risk || {}

    return {
        full_name: profile.user_id || 'Unknown',
        dob: kyc.age ? `Age: ${kyc.age}` : 'Not specified',
        country: kyc.residence_country || kyc.nationality || 'Unknown',
        declared_income: parseFloat(kyc.income) || 0,
        face_match: 94, // Placeholder - not in ML output
        pep: risk.pep_flag || false,
        sanctions: risk.sanctions_status === 'true' || risk.sanctions_status === true,
        document_flags: risk.adverse_media_flag ? ['Adverse media flag'] : []
    }
}

function computeRiskBreakdown(caseAlerts, caseScore = 100) {
    if (!caseAlerts || !Array.isArray(caseAlerts)) return []

    // Group alerts by risk category and compute raw scores
    const categories = {}
    caseAlerts.forEach(alert => {
        const category = alert.evidence?.[0]?.risk_category || alert.signal || 'Other'
        const contribution = Math.abs(alert.evidence?.[0]?.contribution || 0) * 100
        const confidence = parseFloat(alert.confidence) || 0
        const score = Math.round(contribution + (confidence > 1 ? confidence : confidence * 100) / 4)

        if (!categories[category]) {
            categories[category] = 0
        }
        categories[category] += score
    })

    // Convert to array and sort by score
    let breakdown = Object.entries(categories)
        .map(([category, score]) => ({
            category: category.replace(/_/g, ' '),
            rawScore: score
        }))
        .sort((a, b) => b.rawScore - a.rawScore)
        .slice(0, 5)

    // Normalize scores so total equals the case score (max 100)
    const totalRaw = breakdown.reduce((sum, item) => sum + item.rawScore, 0)
    const targetTotal = Math.min(caseScore, 100)

    if (totalRaw > 0) {
        breakdown = breakdown.map(item => ({
            category: item.category,
            score: Math.round((item.rawScore / totalRaw) * targetTotal)
        }))

        // Adjust for rounding errors - add/subtract from largest category
        const currentTotal = breakdown.reduce((sum, item) => sum + item.score, 0)
        if (currentTotal !== targetTotal && breakdown.length > 0) {
            breakdown[0].score += (targetTotal - currentTotal)
        }
    } else {
        breakdown = breakdown.map(item => ({ category: item.category, score: 0 }))
    }

    return breakdown
}

function buildTimeline(txnList, loginList, caseAlerts) {
    const events = []
    let id = 1

    // Add alerts
    if (caseAlerts && Array.isArray(caseAlerts)) {
        caseAlerts.forEach(alert => {
            const date = new Date(alert.event_time)
            events.push({
                id: id++,
                timestamp: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
                description: `Alert: ${alert.signal || 'Anomaly detected'}`,
                source: alert.detector_type || 'ml_anomaly',
                flagged: true,
                sortTime: date.getTime()
            })
        })
    }

    // Add transactions
    if (txnList && Array.isArray(txnList)) {
        txnList.forEach(txn => {
            const date = new Date(txn.event_time)
            const amount = txn.data?.amount || 0
            const type = txn.event_type === 'buy' ? 'Purchase' : txn.event_type === 'sell' ? 'Sale' : txn.event_type
            events.push({
                id: id++,
                timestamp: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
                description: `${type}: $${Math.abs(amount).toLocaleString()} ${txn.data?.stock_id || ''}`,
                source: 'transaction',
                flagged: Math.abs(amount) > 10000,
                sortTime: date.getTime()
            })
        })
    }

    // Add logins
    if (loginList && Array.isArray(loginList)) {
        loginList.forEach(login => {
            const date = new Date(login.event_time)
            const country = login.data?.geo?.country || 'Unknown'
            events.push({
                id: id++,
                timestamp: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
                description: `Login from ${country}`,
                source: 'auth',
                flagged: !login.data?.success,
                sortTime: date.getTime()
            })
        })
    }

    // Sort by time descending
    return events.sort((a, b) => b.sortTime - a.sortTime).slice(0, 20)
}

// ============ FETCH DATA ON MOUNT ============

onMounted(async () => {
    try {
        loading.value = true
        const data = await getInvestigateData(caseId.value)

        // Transform and populate all data
        // Use different names to avoid shadowing the refs (rawStatus, rawProfile, rawTransactions, rawLogins)
        const caseRaw = data.caseData
        const txnRaw = data.transactions
        const loginsRaw = data.logins
        const networkRaw = data.network
        const profileRaw = data.customer
        const statusRaw = data.status

        // Case data
        caseData.value = {
            case_id: caseRaw.case_id,
            risk_level: caseRaw.risk_level?.toLowerCase() || 'medium',
            risk_score: caseRaw.case_score || 0,
            sla_remaining: '4h remaining',
            customer_name: formatUsername(profileRaw?.username) || profileRaw?.user_id || caseRaw.user_id || 'Unknown',
            account_id: profileRaw?.account?.account_id || caseRaw.user_id || '',
            status: caseRaw.status === 'OPEN' ? 'Investigating' : caseRaw.status || 'Unknown',
            related_cases: [] // No related cases in current data
        }

        // Alerts
        alerts.value = transformAlerts(caseRaw.alerts)
        rawAlerts.value = caseRaw.alerts || [] // Keep raw alerts for SHAP chart

        // Transactions
        transactions.value = transformTransactions(txnRaw, statusRaw)
        transactionSummary.value = {
            total_in: statusRaw?.txn?.amount_in_30d || 0,
            total_out: statusRaw?.txn?.amount_out_30d || 0,
            declared_income: parseFloat(profileRaw?.kyc?.income) || 0,
            income_ratio: 0
        }
        // Calculate income ratio
        if (transactionSummary.value.declared_income > 0) {
            transactionSummary.value.income_ratio = Math.round(
                (transactionSummary.value.total_in / transactionSummary.value.declared_income) * 100
            )
        }

        // Logins
        logins.value = transformLogins(loginsRaw, networkRaw)
        loginSummary.value = computeLoginSummary(loginsRaw, networkRaw)

        // Network
        networkConnections.value = transformNetworkConnections(networkRaw)

        // Network Graph - fetch separately and use for summary
        try {
            const graphData = await getCaseNetworkGraph(caseId.value)
            networkGraphData.value = graphData
            // Use graph data for more accurate summary
            networkSummary.value = computeNetworkSummaryFromGraph(graphData, networkRaw)
        } catch (graphError) {
            console.warn('Network graph data not available:', graphError)
            networkGraphData.value = { nodes: [], edges: [] }
            // Fallback to basic network summary
            networkSummary.value = computeNetworkSummary(networkRaw)
        }

        // KYC
        kycData.value = transformKycData(profileRaw)

        // Risk breakdown - normalize to case score
        riskBreakdown.value = computeRiskBreakdown(caseRaw.alerts, caseRaw.case_score || 100)

        // Timeline
        timelineEvents.value = buildTimeline(txnRaw, loginsRaw, caseRaw.alerts)

        // Store raw data for chart components (refs are now correctly populated)
        rawStatus.value = statusRaw || {}
        rawProfile.value = profileRaw || {}
        rawTransactions.value = txnRaw || []
        rawLogins.value = loginsRaw || []

        // Load related cases (hardcoded for CASE-20260207-0001)
        if (caseId.value === 'CASE-20260207-0001') {
            relatedCases.value = [RELATED_CASE_DATA]
        } else {
            relatedCases.value = []
        }

    } catch (e) {
        console.error('Failed to load investigate data:', e)
        error.value = e.message
    } finally {
        loading.value = false
    }
})

const totalRiskScore = computed(() => {
    return riskBreakdown.value.reduce((sum, item) => sum + item.score, 0)
})

const messages = ref([])
const sentinelInitialized = ref(false)

// Generate welcome message with case summary
function generateWelcomeMessage() {
    const riskLevel = caseData.value.risk_level?.toUpperCase() || 'UNKNOWN'
    const riskScore = caseData.value.risk_score || 0
    const alertCount = alerts.value.length
    const highAlerts = alerts.value.filter(a => a.severity === 'high' || a.severity === 'critical').length

    let summary = `Case ${caseData.value.case_id}\n\n`
    summary += `Risk Level: ${riskLevel} (Score: ${riskScore})\n`
    summary += `Active Alerts: ${alertCount} (${highAlerts} high/critical)\n\n`

    if (alerts.value.length > 0) {
        summary += `Here's what flagged this case:\n`
        // Sort by severity (high first) and take top 3
        const sortedAlerts = [...alerts.value].sort((a, b) => {
            const order = { critical: 0, high: 1, med: 2, medium: 2, low: 3 }
            return (order[a.severity] || 4) - (order[b.severity] || 4)
        })
        sortedAlerts.slice(0, 3).forEach(alert => {
            const friendlyDesc = makeFriendlyDescription(alert.description)
            summary += `• ${friendlyDesc}\n`
        })
        summary += '\n'
    }

    summary += `I'm ready to help you investigate this case. Ask me anything.`

    return summary
}

// Convert technical ML descriptions to human-friendly text
function makeFriendlyDescription(description) {
    let friendly = description

    // Remove technical patterns like (net_flow_1d=-50000.00)
    friendly = friendly.replace(/\s*\([^)]*=-?\d+\.?\d*\)/g, '')

    // Remove "This increased/reduced anomaly risk." suffix
    friendly = friendly.replace(/\s*This (increased|reduced) anomaly risk\.?/gi, '')

    // Clean up common technical phrases
    friendly = friendly.replace(/net_flow_1d/gi, 'daily cash flow')
    friendly = friendly.replace(/ewma_resid/gi, 'transaction pattern')
    friendly = friendly.replace(/amount_out_in_1d/gi, 'daily outflow')

    // Make threshold messages friendlier
    friendly = friendly.replace(/exceed threshold value of (\d+\.?\d*)/gi, 'exceeded $$$1 threshold')
    friendly = friendly.replace(/Recent transaction amount/gi, 'Transaction amount')

    // Clean up extra whitespace
    friendly = friendly.replace(/\s+/g, ' ').trim()

    // Remove trailing period if present, we'll handle punctuation
    friendly = friendly.replace(/\.+$/, '')

    return friendly
}

// Methods
function toggleSentinel() {
    sentinelVisible.value = !sentinelVisible.value

    // Add welcome message on first open (after data is loaded)
    if (sentinelVisible.value && !sentinelInitialized.value && !loading.value && caseData.value.case_id) {
        sentinelInitialized.value = true
        messages.value.push({
            id: Date.now(),
            sender: 'bot',
            text: generateWelcomeMessage(),
            timestamp: formatTime(new Date())
        })
    }
}

// Alert expand/collapse functions
function toggleAlert(alertId) {
    if (expandedAlerts.value.has(alertId)) {
        expandedAlerts.value.delete(alertId)
    } else {
        expandedAlerts.value.add(alertId)
    }
    // Trigger reactivity
    expandedAlerts.value = new Set(expandedAlerts.value)
}

function expandAllAlerts() {
    expandedAlerts.value = new Set(alerts.value.map(a => a.alert_id))
}

function collapseAllAlerts() {
    expandedAlerts.value = new Set()
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

function getConfusionMatrixLabel(value) {
    const labels = {
        'TP': 'True Positive',
        'FP': 'False Positive',
        'TN': 'True Negative',
        'FN': 'False Negative'
    }
    return labels[value] || value
}

function getConfusionMatrixDescription(value) {
    const descriptions = {
        'TP': 'Confirmed fraud',
        'FP': 'Not fraud',
        'TN': 'Correctly cleared',
        'FN': 'Missed fraud'
    }
    return descriptions[value] || ''
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

function formatUsername(username) {
    if (!username) return null
    // Convert snake_case to Title Case (e.g., "ahmad_rahman" -> "Ahmad Rahman")
    return username.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

function formatAlertTime(isoString) {
    const date = new Date(isoString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function askAboutEvidence(type, item) {
    // Show AI SENTINEL if hidden
    if (!sentinelVisible.value) {
        toggleSentinel()
    }

    let question = ''
    if (type === 'transaction') {
        // Use eventType if available (e.g., "buy TSLAX"), otherwise use type (deposit/withdrawal)
        const txnType = item.eventType || item.type
        question = `Tell me about the $${item.amount.toLocaleString()} ${txnType} transaction on ${item.date}`
    } else if (type === 'login') {
        question = `Explain the login from ${item.country} on ${item.timestamp}`
    } else if (type === 'network') {
        question = `Tell me about the connection to ${item.account_id} (${item.connection_type})`
    } else if (type === 'timeline') {
        question = `Tell me more about this event: ${item.description}`
    } else if (type === 'related') {
        question = `Tell me about the related case ${item.case_id} with user ${item.user_id}. It has a ${item.similarity_score}% similarity score and is linked via "${item.cluster_type}" pattern. What's the connection to the current case and should they be investigated together?`
    } else if (type === 'related_alert') {
        question = `In the related case ${item.parent_case}, there's an alert "${item.signal}" (${item.severity}): ${item.evidence}. How does this relate to the current case I'm investigating?`
    }

    // Small delay to allow panel to open
    setTimeout(() => {
        sendMessage(question)
    }, 100)
}

// Handler for network graph fullscreen state change
function onNetworkFullscreenChange(isFullscreen) {
    networkGraphFullscreen.value = isFullscreen
}

// Handler for chart clicks
function handleChartAsk(data) {
    // Show AI SENTINEL if hidden
    if (!sentinelVisible.value) {
        sentinelVisible.value = true
    }

    let question = ''
    if (data.type === 'risk') {
        question = `Explain the ${data.category} risk factor that contributed ${data.score} points to the overall risk score. What does this indicate?`
    } else if (data.type === 'shap') {
        const impact = data.contribution > 0 ? 'increased' : 'decreased'
        question = `Explain the "${data.feature}" feature that ${impact} the anomaly risk score by ${Math.abs(data.contribution).toFixed(4)}. ${data.explanation || ''}`
    } else if (data.type === 'radar') {
        question = `Explain the ${data.category} risk dimension showing ${data.value}% risk level. Why is this elevated compared to normal users?`
    } else if (data.type === 'timeline') {
        const event = data.event
        if (data.eventType === 'alert') {
            question = `Tell me about the ${event.label} alert that occurred at ${event.time.toLocaleString()}. What triggered it?`
        } else if (data.eventType === 'transaction') {
            question = `Explain the ${event.label} that occurred at ${event.time.toLocaleString()}. Is this suspicious?`
        } else if (data.eventType === 'login_failed') {
            const riskHint = event.raw?.data?.risk_hint !== 'na' ? event.raw?.data?.risk_hint?.replace(/_/g, ' ') : null
            question = `Analyze this failed login attempt: ${event.label} at ${event.time.toLocaleString()}.${riskHint ? ` Risk indicator: ${riskHint}.` : ''} Is this part of an attack pattern?`
        } else if (data.eventType === 'login_success') {
            question = `Tell me about this successful login: ${event.label} at ${event.time.toLocaleString()}. Was this login legitimate or suspicious?`
        } else if (data.eventType === 'password_change') {
            question = `Analyze this password change event: ${event.label} at ${event.time.toLocaleString()}. Is this potentially unauthorized credential modification?`
        } else if (data.eventType?.startsWith('login')) {
            question = `Tell me about the ${event.label} at ${event.time.toLocaleString()}. Are there any red flags?`
        }
    } else if (data.type === 'network-node') {
        // Handle network graph node clicks
        const nodeType = data.nodeType
        const label = data.label
        const nodeData = data.data || {}
        if (nodeType === 'user') {
            question = `Tell me about user ${label}. What is their account status, occupation (${nodeData.occupation || 'unknown'}), and deposit amount ($${(nodeData.account_deposit || 0).toLocaleString()})? Are there any suspicious patterns?`
        } else if (nodeType === 'ip') {
            const geo = nodeData.geo || {}
            question = `Analyze IP address ${label} located in ${geo.city || 'unknown'}, ${geo.country || 'unknown'}. ${nodeData.vpn_suspected ? 'VPN is suspected.' : ''} Why are ${nodeData.connection_count || 0} users connected through this IP?`
        } else if (nodeType === 'device') {
            question = `Tell me about device ${label}. Is it shared between multiple users? What suspicious activity has been detected on this device?`
        } else if (nodeType === 'stock') {
            question = `Analyze the trading activity on ${label}. Total volume: $${(nodeData.total_volume || 0).toLocaleString()}, trades: ${nodeData.trade_count || 0}. Is there evidence of manipulation?`
        } else {
            question = `Tell me about this ${nodeType} entity: ${label}. What is its role in this case?`
        }
    } else if (data.type === 'network-edge') {
        // Handle network graph edge clicks
        const relation = data.relation?.replace(/_/g, ' ') || 'connection'
        const source = data.source?.split(':')[1] || 'unknown'
        const target = data.target?.split(':')[1] || 'unknown'
        const edgeData = data.data || {}
        const eventType = data.eventType?.toUpperCase() || 'EVENT'
        question = `Explain the ${relation} between ${source} and ${target}. Event type: ${eventType}, Amount: $${(edgeData.amount || 0).toLocaleString()}${edgeData.stock_id ? `, Stock: ${edgeData.stock_id}` : ''}. Is this connection suspicious?`
    }

    setTimeout(() => {
        sendMessage(question)
    }, 100)
}

function extractFollowUpQuestions(text) {
    // Extract follow-up questions from the response text
    const questions = []

    // Look for "Follow-up Questions:" section
    const patterns = [
        /(?:Follow-up Questions?|Suggested Follow-up Questions?):?\s*\n([\s\S]*?)(?:\n\n|$)/i,
        /\*\*(?:Follow-up Questions?|Suggested Follow-up Questions?):?\*\*\s*\n([\s\S]*?)(?:\n\n|$)/i
    ]

    for (const pattern of patterns) {
        const match = text.match(pattern)
        if (match && match[1]) {
            // Extract individual questions (lines starting with - or numbers)
            const lines = match[1].split('\n')
            for (const line of lines) {
                const cleaned = line
                    .replace(/^[\s\-\*\d\.]+/, '') // Remove leading markers
                    .replace(/\*\*/g, '') // Remove bold
                    .trim()
                if (cleaned && cleaned.length > 10 && cleaned.endsWith('?')) {
                    questions.push(cleaned)
                }
            }
        }
    }

    return questions.slice(0, 4) // Max 4 questions
}

function cleanResponseText(text) {
    // Remove "Follow-up Questions" section and everything after
    let cleaned = text
        .replace(/---\s*\n?\*?\*?(?:Suggested )?Follow-up Questions:?\*?\*?[\s\S]*$/i, '')
        .replace(/\*\*(?:Suggested )?Follow-up Questions:?\*\*[\s\S]*$/i, '')
        .replace(/(?:Suggested )?Follow-up Questions:[\s\S]*$/i, '')

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

        // Extract follow-up questions from raw response BEFORE cleaning
        const extractedQuestions = extractFollowUpQuestions(response.response)

        // Clean the response text (removes follow-up questions section)
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

        // Update suggested questions - prefer extracted from text, fallback to API response
        if (extractedQuestions.length > 0) {
            suggestedQuestions.value = extractedQuestions
        } else if (response.suggested_questions && response.suggested_questions.length > 0) {
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

function openCommentModal(type) {
    decisionType.value = type
    commentText.value = ''
    showCommentModal.value = true
}

function closeCommentModal() {
    showCommentModal.value = false
    commentText.value = ''
    decisionType.value = ''
}

function submitDecision() {
    console.log('Submitting decision:', {
        type: decisionType.value,
        comment: commentText.value,
        caseId: caseId.value
    })
    // TODO: Call API to submit the decision
    closeCommentModal()
}
</script>

<style scoped>
@keyframes bounce {

    0%,
    100% {
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
