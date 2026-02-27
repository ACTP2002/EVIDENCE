<!-- cases/[id]/report.vue - Dynamic Report -->

<template>
    <div class="min-h-screen bg-gray-50">
        <!-- Loading State -->
        <div v-if="loading" class="min-h-screen flex items-center justify-center">
            <div class="text-center">
                <div class="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p class="text-slate-600">Generating investigation report...</p>
            </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="min-h-screen flex items-center justify-center">
            <div class="text-center max-w-md">
                <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" class="text-red-500">
                        <path d="M12 8V12M12 16V16.5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
                        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" />
                    </svg>
                </div>
                <h2 class="text-xl font-bold text-slate-900 mb-2">Failed to Load Report</h2>
                <p class="text-slate-600 mb-4">{{ error }}</p>
                <button @click="fetchInvestigation({ includeReport: true, includeRegulatory: true })"
                    class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-light transition-all">
                    Retry
                </button>
            </div>
        </div>

        <!-- Report Content -->
        <template v-else-if="data">
            <!-- Header -->
            <header class="bg-white border-b border-gray-200 px-10 py-6 sticky top-0 z-10">
                <div class="max-w-[1200px] mx-auto flex justify-between items-center">
                    <div class="flex items-center gap-5">
                        <button
                            class="w-10 h-10 rounded-lg border border-gray-200 flex items-center justify-center text-slate-400 hover:bg-gray-50 hover:border-gray-300 hover:text-slate-900 transition-all"
                            @click="navigateTo(`/cases/${caseId}`)">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M12 16L6 10L12 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" />
                            </svg>
                        </button>
                        <div>
                            <h1 class="text-xl font-bold text-slate-900">Investigation Report</h1>
                            <p class="text-[13px] text-slate-500 font-mono">Case {{ caseId }} &bull; Generated {{ formatDate(report?.generated_at) }}</p>
                        </div>
                    </div>
                    <div class="flex gap-3">
                        <button
                            class="px-4 py-2.5 bg-white border border-gray-200 rounded-lg text-sm font-semibold text-slate-500 hover:border-gray-300 hover:text-slate-900 transition-all flex items-center gap-2">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <path d="M14 10V12.5C14 13.3284 13.3284 14 12.5 14H3.5C2.67157 14 2 13.3284 2 12.5V10"
                                    stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                                <path d="M8 2V10M8 10L11 7M8 10L5 7" stroke="currentColor" stroke-width="1.5"
                                    stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                            Download PDF
                        </button>
                        <button
                            class="px-4 py-2.5 bg-primary rounded-lg text-sm font-semibold text-white hover:bg-primary-light transition-all flex items-center gap-2">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <path d="M8 2L12 6H9V14H7V6H4L8 2Z" fill="currentColor" />
                            </svg>
                            Send to Compliance
                        </button>
                    </div>
                </div>
            </header>

            <!-- Report Content -->
            <div class="py-10 px-10">
                <div class="max-w-[1000px] mx-auto">
                    <!-- Report Document -->
                    <div class="bg-white rounded-xl shadow-lg-custom p-16">

                        <!-- Document Header -->
                        <div class="border-b-[3px] border-primary pb-8 mb-10">
                            <div class="flex items-start gap-5 mb-8">
                                <svg width="40" height="40" viewBox="0 0 40 40" fill="none" class="flex-shrink-0">
                                    <rect width="40" height="40" rx="10" fill="url(#report-logo-gradient)" />
                                    <path d="M20 10L27.5 15V25L20 30L12.5 25V15L20 10Z" stroke="white" stroke-width="2.5"
                                        stroke-linejoin="round" />
                                    <circle cx="20" cy="20" r="2.5" fill="white" />
                                    <defs>
                                        <linearGradient id="report-logo-gradient" x1="0" y1="0" x2="40" y2="40">
                                            <stop stop-color="#00D4FF" />
                                            <stop offset="1" stop-color="#0A2540" />
                                        </linearGradient>
                                    </defs>
                                </svg>
                                <div>
                                    <div class="text-[22px] font-bold text-slate-900 mb-1">SENTINEL Investigation
                                        Platform</div>
                                    <div class="text-[13px] text-slate-400 uppercase tracking-wider font-semibold">
                                        Compliance & Risk Management Division</div>
                                </div>
                            </div>

                            <div class="grid grid-cols-3 gap-5">
                                <div>
                                    <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Report Type</div>
                                    <div class="text-sm text-slate-900 font-semibold">{{ formatReportType(report?.report_type) }}</div>
                                </div>
                                <div>
                                    <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Case ID</div>
                                    <div class="text-sm text-slate-900 font-semibold font-mono">{{ caseId }}</div>
                                </div>
                                <div>
                                    <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Generated</div>
                                    <div class="text-sm text-slate-900 font-semibold">{{ formatDateTime(report?.generated_at) }}</div>
                                </div>
                                <div>
                                    <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Subject</div>
                                    <div class="text-sm text-slate-900 font-semibold">{{ formatUsername(profile?.username) || profile?.user_id || 'N/A' }}</div>
                                </div>
                                <div>
                                    <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Classification</div>
                                    <div class="text-sm text-risk-high font-bold">CONFIDENTIAL</div>
                                </div>
                                <div>
                                    <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Status</div>
                                    <div class="text-sm font-bold" :class="statusClass">{{ caseContext?.case_info?.status || 'UNDER INVESTIGATION' }}</div>
                                </div>
                            </div>
                        </div>

                        <!-- Executive Summary -->
                        <section class="mb-12">
                            <h2 class="text-xl font-bold text-slate-900 mb-6 pb-3 border-b-2 border-gray-100">Executive Summary</h2>

                            <div class="flex items-start gap-4 p-5 rounded-lg mb-6" :class="riskLevelBgClass + ' border-2'">
                                <div class="w-12 h-12 rounded-lg text-white flex items-center justify-center flex-shrink-0"
                                    :class="riskLevelBg">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                        <path d="M12 8V12M12 16V16.5" stroke="currentColor" stroke-width="2.5"
                                            stroke-linecap="round" />
                                        <path d="M3 18L12 4L21 18H3Z" stroke="currentColor" stroke-width="2"
                                            stroke-linejoin="round" />
                                    </svg>
                                </div>
                                <div>
                                    <div class="text-base font-bold font-mono mb-1" :class="riskLevelClass">
                                        {{ (riskDecomposition?.risk_level || caseContext?.case_info?.risk_level || 'UNKNOWN').toUpperCase() }} RISK LEVEL -
                                        RISK SCORE: {{ riskDecomposition?.overall_risk_score || caseContext?.case_info?.case_score || 0 }}/100
                                    </div>
                                    <div class="text-sm text-slate-600">
                                        {{ dashboardSummary?.headline || 'Investigation in progress' }}
                                    </div>
                                </div>
                            </div>

                            <div class="text-sm leading-relaxed text-slate-900 whitespace-pre-line">
                                {{ report?.executive_summary || 'Executive summary not available.' }}
                            </div>
                        </section>

                        <!-- Subject Information -->
                        <section class="mb-12">
                            <h2 class="text-xl font-bold text-slate-900 mb-6 pb-3 border-b-2 border-gray-100">Subject Information</h2>

                            <div class="space-y-4">
                                <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                    <div class="text-[13px] font-semibold text-slate-400">User ID</div>
                                    <div class="text-sm text-slate-900 font-mono">{{ profile?.user_id || 'N/A' }}</div>
                                </div>
                                <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                    <div class="text-[13px] font-semibold text-slate-400">Username</div>
                                    <div class="text-sm text-slate-900 font-semibold">{{ formatUsername(profile?.username) || 'N/A' }}</div>
                                </div>
                                <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                    <div class="text-[13px] font-semibold text-slate-400">Account ID</div>
                                    <div class="text-sm text-slate-900 font-mono">{{ profile?.account?.account_id || 'N/A' }}</div>
                                </div>
                                <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                    <div class="text-[13px] font-semibold text-slate-400">Account Status</div>
                                    <div class="text-sm text-slate-900 font-semibold">{{ profile?.account?.account_status || 'N/A' }}</div>
                                </div>
                                <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                    <div class="text-[13px] font-semibold text-slate-400">KYC Level</div>
                                    <div class="text-sm text-slate-900">{{ profile?.kyc?.kyc_level || 'N/A' }}</div>
                                </div>
                                <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                    <div class="text-[13px] font-semibold text-slate-400">Nationality</div>
                                    <div class="text-sm text-slate-900">{{ profile?.kyc?.nationality || 'N/A' }}</div>
                                </div>
                                <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                    <div class="text-[13px] font-semibold text-slate-400">Residence Country</div>
                                    <div class="text-sm text-slate-900">{{ profile?.kyc?.residence_country || 'N/A' }}</div>
                                </div>
                                <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                    <div class="text-[13px] font-semibold text-slate-400">Occupation</div>
                                    <div class="text-sm text-slate-900">{{ profile?.kyc?.occupation || 'N/A' }}</div>
                                </div>
                                <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                    <div class="text-[13px] font-semibold text-slate-400">Declared Monthly Income</div>
                                    <div class="text-sm text-slate-900">${{ formatNumber(profile?.kyc?.income) }} USD</div>
                                </div>
                                <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                    <div class="text-[13px] font-semibold text-slate-400">Account Deposit</div>
                                    <div class="text-sm text-slate-900">${{ formatNumber(profile?.account?.account_deposit) }} USD</div>
                                </div>
                                <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                    <div class="text-[13px] font-semibold text-slate-400">PEP Flag</div>
                                    <div class="text-sm" :class="profile?.risk?.pep_flag ? 'text-risk-high font-bold' : 'text-slate-900'">
                                        {{ profile?.risk?.pep_flag ? 'YES' : 'No' }}
                                    </div>
                                </div>
                                <div class="grid grid-cols-[220px_1fr] gap-5">
                                    <div class="text-[13px] font-semibold text-slate-400">Sanctions Status</div>
                                    <div class="text-sm" :class="profile?.risk?.sanctions_status === 'true' ? 'text-risk-critical font-bold' : 'text-slate-900'">
                                        {{ profile?.risk?.sanctions_status === 'true' ? 'FLAGGED' : 'Clear' }}
                                    </div>
                                </div>
                            </div>
                        </section>

                        <!-- Risk Indicators -->
                        <section class="mb-12">
                            <h2 class="text-xl font-bold text-slate-900 mb-6 pb-3 border-b-2 border-gray-100">Risk
                                Indicators Analysis</h2>

                            <!-- Dynamic Risk Indicators from alerts -->
                            <div v-for="(alert, index) in caseContext?.alerts" :key="alert.alert_id"
                                class="border-l-4 p-6 rounded-r-lg mb-8"
                                :class="getAlertBorderClass(alert.severity)">
                                <div class="flex justify-between items-center mb-4">
                                    <div class="text-[11px] uppercase tracking-wider font-bold"
                                        :class="getAlertTextClass(alert.severity)">{{ alert.severity }} SEVERITY</div>
                                    <div class="text-xs font-mono font-semibold text-slate-400">Risk Impact: +{{ Math.round(parseFloat(alert.confidence) * 100 / caseContext.alerts.length) }} points
                                    </div>
                                </div>
                                <h3 class="text-base font-bold text-slate-900 mb-4">{{ alert.signal }}</h3>
                                <p class="text-sm leading-relaxed text-slate-900 mb-5">
                                    {{ getAlertDescription(alert) }}
                                </p>
                                <div v-if="alert.evidence?.length" class="bg-white p-4 rounded-lg mb-5">
                                    <div class="text-[13px] font-bold text-slate-900 mb-3">Supporting Evidence:</div>
                                    <ul class="list-inside list-disc space-y-1.5">
                                        <li v-for="(ev, eIndex) in alert.evidence" :key="eIndex"
                                            class="text-[13px] leading-relaxed text-slate-600">
                                            {{ ev.feature }}: {{ ev.explanation }}
                                        </li>
                                    </ul>
                                </div>
                                <p class="text-sm leading-relaxed text-slate-900">
                                    <strong>Assessment:</strong> {{ getAlertAssessment(alert) }}
                                </p>
                            </div>
                        </section>

                        <!-- Timeline -->
                        <section class="mb-12">
                            <h2 class="text-xl font-bold text-slate-900 mb-6 pb-3 border-b-2 border-gray-100">Investigation
                                Timeline</h2>

                            <div class="space-y-7">
                                <div v-for="(event, index) in timelineEvents" :key="index" class="relative pl-7">
                                    <div
                                        class="absolute left-0 top-1 w-4 h-4 rounded-full bg-accent border-[3px] border-white shadow-[0_0_0_2px_#E4E7EB]">
                                    </div>
                                    <div v-if="index < timelineEvents.length - 1" class="absolute left-[7px] top-5 bottom-[-28px] w-0.5 bg-gray-200"></div>
                                    <div class="text-xs font-mono text-slate-400 mb-1.5">{{ formatDateTime(event.time) }}
                                    </div>
                                    <div class="text-[15px] font-bold text-slate-900 mb-2">{{ event.title }}</div>
                                    <div class="text-[13px] leading-relaxed text-slate-600">
                                        {{ event.description }}
                                    </div>
                                </div>
                            </div>
                        </section>

                        <!-- Network Analysis -->
                        <section class="mb-12">
                            <h2 class="text-xl font-bold text-slate-900 mb-6 pb-3 border-b-2 border-gray-100">Network
                                Analysis</h2>

                            <p class="text-sm leading-relaxed text-slate-900 mb-6">
                                Cross-account forensic analysis reveals subject account connections to other entities.
                                Multiple technical and behavioral connections identified to other accounts
                                currently under investigation or previously confirmed as fraudulent.
                            </p>

                            <div class="grid grid-cols-3 gap-5 my-6">
                                <div class="p-5 bg-white border-2 border-gray-200 rounded-lg text-center">
                                    <div class="text-[28px] font-bold font-mono text-risk-critical mb-2">{{ networkStats.sharedDevices }} Accounts</div>
                                    <div class="text-[13px] font-semibold text-slate-900 mb-1.5">Shared Device Fingerprint
                                    </div>
                                    <div class="text-xs text-slate-400">Device ID: {{ networkStats.deviceId }}</div>
                                </div>
                                <div class="p-5 bg-white border-2 border-gray-200 rounded-lg text-center">
                                    <div class="text-[28px] font-bold font-mono text-risk-critical mb-2">{{ networkStats.sharedIPs }} Accounts</div>
                                    <div class="text-[13px] font-semibold text-slate-900 mb-1.5">Shared IP Addresses</div>
                                    <div class="text-xs text-slate-400">During overlapping time periods</div>
                                </div>
                                <div class="p-5 bg-white border-2 border-gray-200 rounded-lg text-center">
                                    <div class="text-[28px] font-bold font-mono text-risk-critical mb-2">{{ networkStats.coordination }}</div>
                                    <div class="text-[13px] font-semibold text-slate-900 mb-1.5">Transaction Timing</div>
                                    <div class="text-xs text-slate-400">{{ networkStats.coordinationDetail }}</div>
                                </div>
                            </div>

                            <p class="text-sm leading-relaxed text-slate-900">
                                <strong>Network Assessment:</strong> {{ networkAssessment }}
                            </p>
                        </section>

                        <!-- Conclusions -->
                        <section class="mb-12">
                            <h2 class="text-xl font-bold text-slate-900 mb-6 pb-3 border-b-2 border-gray-100">Conclusions &
                                Recommendations</h2>

                            <div class="mb-8">
                                <h3 class="text-base font-bold text-slate-900 mb-4">Findings</h3>
                                <ol class="list-decimal list-inside space-y-3">
                                    <li v-for="(finding, index) in findings" :key="index"
                                        class="text-sm leading-relaxed text-slate-900">{{ finding }}</li>
                                </ol>
                            </div>

                            <div>
                                <h3 class="text-base font-bold text-slate-900 mb-4">Recommended Actions</h3>
                                <ol class="list-decimal list-inside space-y-3">
                                    <li v-for="(rec, index) in recommendedActions" :key="index"
                                        class="text-sm leading-relaxed text-slate-900" v-html="rec"></li>
                                </ol>
                            </div>
                        </section>

                        <!-- Footer -->
                        <div class="pt-6 mt-12">
                            <div class="h-0.5 bg-primary mb-5"></div>
                            <div class="grid grid-cols-3 gap-5 mb-4">
                                <div>
                                    <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Generated by</div>
                                    <div class="text-xs text-slate-600 font-semibold">SENTINEL AI Investigation Platform</div>
                                </div>
                                <div>
                                    <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Report ID</div>
                                    <div class="text-xs text-slate-600 font-semibold font-mono">{{ report?.report_id || data?.investigation_id || 'N/A' }}</div>
                                </div>
                                <div>
                                    <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Investigation Duration</div>
                                    <div class="text-xs text-slate-600 font-semibold">{{ data?.total_duration_ms ? (data.total_duration_ms / 1000).toFixed(2) + 's' : 'N/A' }}</div>
                                </div>
                            </div>
                            <div class="flex items-center justify-center gap-2 p-3 bg-orange-50 rounded-lg">
                                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                                    <path d="M7 1L9 5L13 5.5L10 8.5L11 13L7 11L3 13L4 8.5L1 5.5L5 5L7 1Z"
                                        fill="currentColor" class="text-risk-high" />
                                </svg>
                                <span class="text-[11px] font-bold text-risk-high uppercase tracking-wider">
                                    CONFIDENTIAL - FOR AUTHORIZED PERSONNEL ONLY
                                </span>
                            </div>
                        </div>

                    </div>
                </div>
            </div>

            <!-- Chatbot Button -->
            <button @click="toggleChat"
                class="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-accent to-primary rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center z-50 group"
                :class="{ 'scale-0': isChatOpen }">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" class="text-white">
                    <path
                        d="M8 12H8.01M12 12H12.01M16 12H16.01M21 12C21 16.4183 16.9706 20 12 20C10.4607 20 9.01172 19.6565 7.74467 19.0511L3 20L4.39499 16.28C3.51156 15.0423 3 13.5743 3 12C3 7.58172 7.02944 4 12 4C16.9706 4 21 7.58172 21 12Z"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <span
                    class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white text-xs font-bold animate-pulse">
                    1
                </span>
            </button>

            <!-- Chatbot Window -->
            <div v-show="isChatOpen"
                class="fixed bottom-6 right-6 w-[380px] h-[600px] bg-white rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden transition-all duration-300"
                :class="{ 'scale-0': !isChatOpen, 'scale-100': isChatOpen }">
                <!-- Chat Header -->
                <div class="bg-gradient-to-r from-accent to-primary p-4 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M10 2L15 6V14L10 18L5 14V6L10 2Z" stroke="white" stroke-width="2"
                                    stroke-linejoin="round" />
                                <circle cx="10" cy="10" r="1.5" fill="white" />
                            </svg>
                        </div>
                        <div>
                            <div class="text-white font-semibold text-sm">AI Assistant</div>
                            <div class="text-white/80 text-xs">Active</div>
                        </div>
                    </div>
                    <button @click="toggleChat"
                        class="w-8 h-8 rounded-full hover:bg-white/20 flex items-center justify-center transition-colors">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M15 5L5 15M5 5L15 15" stroke="white" stroke-width="2" stroke-linecap="round" />
                        </svg>
                    </button>
                </div>

                <!-- Messages Container -->
                <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                    <div v-for="message in messages" :key="message.id" :class="[
                        'flex',
                        message.sender === 'user' ? 'justify-end' : 'justify-start'
                    ]">
                        <div :class="[
                            'max-w-[80%] rounded-2xl px-4 py-2.5 text-sm',
                            message.sender === 'user'
                                ? 'bg-primary text-white rounded-br-sm'
                                : 'bg-white text-slate-900 shadow-sm rounded-bl-sm'
                        ]">
                            <div class="leading-relaxed">{{ message.text }}</div>
                            <div :class="[
                                'text-xs mt-1',
                                message.sender === 'user' ? 'text-white/70' : 'text-slate-400'
                            ]">
                                {{ new Date(message.timestamp).toLocaleTimeString([], {
                                    hour: '2-digit', minute: '2-digit'
                                }) }}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Suggested Questions -->
                <div class="px-4 py-2 bg-white border-t border-gray-100">
                    <div class="text-xs text-slate-400 mb-2">Quick questions:</div>
                    <div class="flex flex-wrap gap-2">
                        <button @click="userMessage = 'What is the risk score?'; sendMessage()"
                            class="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-xs text-slate-700 transition-colors">
                            Risk Score
                        </button>
                        <button @click="userMessage = 'Show evidence'; sendMessage()"
                            class="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-xs text-slate-700 transition-colors">
                            Evidence
                        </button>
                        <button @click="userMessage = 'Network connections'; sendMessage()"
                            class="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-xs text-slate-700 transition-colors">
                            Network
                        </button>
                    </div>
                </div>

                <!-- Input Area -->
                <div class="p-4 bg-white border-t border-gray-200">
                    <div class="flex gap-2">
                        <input v-model="userMessage" @keypress="handleKeyPress" type="text"
                            placeholder="Ask about this case..."
                            class="flex-1 px-4 py-2.5 border border-gray-200 rounded-full text-sm focus:outline-none focus:border-primary transition-colors" />
                        <button @click="sendMessage" :disabled="!userMessage.trim()"
                            class="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-white hover:bg-primary-light transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                                <path d="M16 2L8 10M16 2L11 16L8 10M16 2L2 7L8 10" stroke="currentColor" stroke-width="2"
                                    stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </template>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const caseId = computed(() => route.params.id || 'UNKNOWN')

// Use the investigation composable
const {
    data,
    loading,
    error,
    fetchInvestigation,
    caseContext,
    profile,
    riskDecomposition,
    timeline,
    networkAnalysis,
    report,
    recommendations,
    dashboardSummary,
    riskLevelClass,
    riskLevelBgClass
} = useInvestigation(caseId)

// Fetch data on mount
onMounted(() => {
    fetchInvestigation({ includeReport: true, includeRegulatory: true })
})

// Risk level background color
const riskLevelBg = computed(() => {
    const level = (riskDecomposition.value?.risk_level || caseContext.value?.case_info?.risk_level || '').toLowerCase()
    switch (level) {
        case 'critical': return 'bg-risk-critical'
        case 'high': return 'bg-risk-high'
        case 'medium': return 'bg-yellow-500'
        case 'low': return 'bg-green-500'
        default: return 'bg-slate-500'
    }
})

// Status styling
const statusClass = computed(() => {
    const status = caseContext.value?.case_info?.status?.toLowerCase()
    switch (status) {
        case 'open': return 'text-status-open'
        case 'escalated': return 'text-risk-critical'
        case 'investigating': return 'text-yellow-600'
        case 'closed': return 'text-green-600'
        default: return 'text-slate-600'
    }
})

// Formatting helpers
const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A'
    return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    })
}

const formatDateTime = (dateStr) => {
    if (!dateStr) return 'N/A'
    return new Date(dateStr).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
    })
}

const formatNumber = (num) => {
    if (!num) return '0'
    return parseFloat(num).toLocaleString()
}

const formatReportType = (type) => {
    if (!type) return 'Investigation Summary'
    return type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

const formatUsername = (username) => {
    if (!username) return null
    // Convert snake_case to Title Case (e.g., "ahmad_rahman" -> "Ahmad Rahman")
    return username.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

const formatEventDetails = (details) => {
    if (!details) return ''
    if (typeof details === 'string') return details
    return Object.entries(details)
        .map(([key, value]) => `${key}: ${value}`)
        .join(', ')
}

// Risk component styling helpers
const getComponentBorderClass = (score) => {
    if (score >= 80) return 'border-risk-critical bg-red-50'
    if (score >= 60) return 'border-risk-high bg-orange-50'
    if (score >= 40) return 'border-yellow-500 bg-yellow-50'
    return 'border-green-500 bg-green-50'
}

const getComponentTextClass = (score) => {
    if (score >= 80) return 'text-risk-critical'
    if (score >= 60) return 'text-risk-high'
    if (score >= 40) return 'text-yellow-600'
    return 'text-green-600'
}

const getSeverityLabel = (score) => {
    if (score >= 80) return 'CRITICAL'
    if (score >= 60) return 'HIGH'
    if (score >= 40) return 'MEDIUM'
    return 'LOW'
}

// Alert styling helpers
const getAlertBorderClass = (severity) => {
    switch (severity?.toUpperCase()) {
        case 'CRITICAL': return 'border-risk-critical bg-red-50'
        case 'HIGH': return 'border-risk-high bg-orange-50'
        case 'MED':
        case 'MEDIUM': return 'border-yellow-500 bg-yellow-50'
        default: return 'border-green-500 bg-green-50'
    }
}

const getAlertTextClass = (severity) => {
    switch (severity?.toUpperCase()) {
        case 'CRITICAL': return 'text-risk-critical'
        case 'HIGH': return 'text-risk-high'
        case 'MED':
        case 'MEDIUM': return 'text-yellow-600'
        default: return 'text-green-600'
    }
}

// Timeline styling
const getTimelineDotClass = (severity) => {
    switch (severity?.toLowerCase()) {
        case 'critical': return 'bg-risk-critical'
        case 'warning': return 'bg-risk-high'
        default: return 'bg-accent'
    }
}

// Generate alert description based on signal type
const getAlertDescription = (alert) => {
    const signalDescriptions = {
        'Monetary Deviation': `Subject's transaction patterns show significant deviation from declared financial profile. The transaction amount and frequency exceed expected thresholds based on account history and declared income.`,
        'Liquidity Shift': `Analysis detected unusual cash flow patterns indicating potential fund movement inconsistent with normal account behavior. Daily net flow shows significant shifts that warrant investigation.`,
        'Multi-Accounting': `Graph analysis detected patterns consistent with multiple account control. Device and IP sharing patterns suggest coordinated account activity.`,
        'Brute Force Attack': `Multiple failed authentication attempts detected within a short time window, originating from multiple IP addresses. Pattern consistent with credential stuffing or brute force attack.`,
        'Geo Velocity Anomaly': `Login activity detected from geographically distant locations within an impossibly short time frame, indicating potential account compromise or VPN usage.`,
        'Credential Change': `Security credentials were modified shortly after suspicious authentication events, a pattern commonly associated with account takeover attacks.`,
        'Rapid Liquidation': `Significant portion of account balance withdrawn in rapid succession following suspicious authentication events.`,
        'Structuring Pattern': `Multiple transactions detected at amounts strategically below reporting thresholds, a pattern consistent with structuring to avoid regulatory detection.`,
        'Temporal Pattern': `Transactions occur at suspiciously regular intervals, suggesting automated or coordinated activity.`,
        'Source Mismatch': `Transaction volumes significantly inconsistent with declared source of funds and income profile.`,
        'Wash Trading Pattern': `Round-trip trades detected within short time windows, suggesting artificial volume generation.`,
        'Coordinated Trading': `High concentration of trades with specific counterparties, with statistical improbability suggesting coordinated activity.`,
        'Artificial Volume': `Trading activity contributed disproportionately to market volume with minimal price impact, consistent with wash trading.`
    }
    return signalDescriptions[alert.signal] || `Alert triggered for ${alert.signal} with ${alert.detector_type} detection. Confidence level: ${(parseFloat(alert.confidence) * 100).toFixed(1)}%.`
}

// Generate alert assessment
const getAlertAssessment = (alert) => {
    const severity = alert.severity?.toUpperCase()
    const confidence = parseFloat(alert.confidence)

    if (severity === 'CRITICAL' || severity === 'HIGH') {
        return `This ${severity.toLowerCase()}-severity indicator requires immediate attention. The detection confidence of ${(confidence * 100).toFixed(1)}% suggests high reliability. Pattern analysis indicates behavior consistent with known fraud typologies. Recommend escalation for senior review.`
    } else if (severity === 'MED' || severity === 'MEDIUM') {
        return `This medium-severity indicator warrants further investigation. While not immediately conclusive, the pattern should be monitored for escalation. Consider gathering additional evidence before taking action.`
    }
    return `This indicator has been flagged for awareness. While lower severity, it contributes to the overall risk profile and should be considered in conjunction with other findings.`
}

// Build timeline events from alerts and case data
const timelineEvents = computed(() => {
    const events = []
    const alerts = caseContext.value?.alerts || []
    const caseInfo = caseContext.value?.case_info

    // Add alert events
    alerts.forEach(alert => {
        events.push({
            time: alert.event_time,
            title: alert.signal,
            description: `${alert.detector_type} detection triggered with ${alert.severity} severity. Confidence: ${(parseFloat(alert.confidence) * 100).toFixed(1)}%. ${alert.evidence?.[0]?.explanation || ''}`
        })
    })

    // Add case opened event
    if (caseInfo?.opened_at) {
        events.push({
            time: caseInfo.opened_at,
            title: 'Case Opened',
            description: `Investigation case ${caseInfo.case_id} opened with initial risk score of ${caseInfo.case_score}/100. Status: ${caseInfo.status}.`
        })
    }

    // Add investigation completed event
    if (data.value?.completed_at) {
        events.push({
            time: data.value.completed_at,
            title: 'AI Investigation Completed',
            description: `Automated investigation completed. ${data.value.skills_executed?.length || 0} analysis skills executed. Report generated for compliance review.`
        })
    }

    // Sort by time
    return events.sort((a, b) => new Date(a.time) - new Date(b.time))
})

// Network statistics
const networkStats = computed(() => {
    const na = networkAnalysis.value
    const ctx = caseContext.value

    // Try to extract from network analysis or generate from case data
    const entities = na?.entities?.length || 0
    const clusters = na?.clusters?.length || 0

    // Generate device ID from case context if available
    const deviceIds = [...new Set(ctx?.logins?.map(l => l.device_id) || [])]
    const uniqueIPs = [...new Set(ctx?.logins?.map(l => l.ip) || [])]

    return {
        sharedDevices: na?.risk_summary?.shared_device_count || Math.max(1, deviceIds.length),
        deviceId: deviceIds[0] || 'N/A',
        sharedIPs: na?.risk_summary?.shared_ip_count || Math.max(1, uniqueIPs.length),
        coordination: na?.risk_summary?.coordination_detected ? 'Coordinated' : 'Under Analysis',
        coordinationDetail: na?.risk_summary?.coordination_window || 'Transaction timing analysis pending'
    }
})

// Network assessment text
const networkAssessment = computed(() => {
    const na = networkAnalysis.value
    const riskLevel = riskDecomposition.value?.risk_level?.toUpperCase()

    if (na?.risk_summary?.fraud_ring_detected) {
        return `Evidence strongly suggests organized fraud operation involving multiple controlled accounts operating in coordination. Recommend expanding investigation to all linked accounts and implementing coordinated enforcement action.`
    } else if (riskLevel === 'CRITICAL' || riskLevel === 'HIGH') {
        return `Network analysis reveals connections that warrant further investigation. While definitive fraud ring classification is pending, the entity relationships and transaction patterns suggest coordinated activity. Recommend monitoring linked accounts.`
    }
    return `Network analysis completed. Connections identified are within normal parameters for account activity. Continue standard monitoring procedures.`
})

// Generate findings from case data
const findings = computed(() => {
    const ctx = caseContext.value
    const rd = riskDecomposition.value
    const alerts = ctx?.alerts || []
    const findingsList = []

    // Overall risk finding
    if (rd?.overall_risk_score) {
        findingsList.push(`Subject account exhibits ${alerts.length} alert indicators with composite risk score of ${rd.overall_risk_score}/100, classified as ${rd.risk_level?.toUpperCase()} risk.`)
    }

    // Add findings from key differentiators
    rd?.key_differentiators?.forEach(diff => {
        findingsList.push(diff)
    })

    // Add findings from report key_findings
    report.value?.key_findings?.forEach(finding => {
        if (!findingsList.includes(finding)) {
            findingsList.push(finding)
        }
    })

    // Generate from alerts if needed
    if (findingsList.length < 3) {
        alerts.slice(0, 3).forEach(alert => {
            const finding = `${alert.signal} detected by ${alert.detector_type} with ${alert.severity} severity and ${(parseFloat(alert.confidence) * 100).toFixed(1)}% confidence.`
            if (!findingsList.some(f => f.includes(alert.signal))) {
                findingsList.push(finding)
            }
        })
    }

    return findingsList.slice(0, 6)
})

// Generate recommended actions
const recommendedActions = computed(() => {
    const recs = recommendations.value?.recommendations || []
    const reportRecs = report.value?.recommendations || []
    const riskLevel = riskDecomposition.value?.risk_level?.toUpperCase()

    // If we have recommendations from API, use those
    if (recs.length > 0) {
        return recs.map(r => `<strong>${r.action}</strong> - ${r.rationale || 'Priority: ' + r.priority}`)
    }

    if (reportRecs.length > 0) {
        return reportRecs.map(r => typeof r === 'string' ? r : `<strong>${r}</strong>`)
    }

    // Generate default recommendations based on risk level
    const defaultRecs = []
    if (riskLevel === 'CRITICAL') {
        defaultRecs.push('<strong>Immediate account suspension</strong> - Prevent further potentially fraudulent transactions')
        defaultRecs.push('<strong>Asset freeze</strong> - Preserve evidence and prevent dissipation of funds')
        defaultRecs.push('<strong>Regulatory reporting</strong> - File Suspicious Activity Report (SAR) with relevant authorities')
        defaultRecs.push('<strong>Law enforcement referral</strong> - Coordinate with financial crimes task force')
    } else if (riskLevel === 'HIGH') {
        defaultRecs.push('<strong>Enhanced monitoring</strong> - Implement real-time transaction monitoring')
        defaultRecs.push('<strong>Account restrictions</strong> - Limit transaction capabilities pending review')
        defaultRecs.push('<strong>Customer verification</strong> - Conduct enhanced due diligence on identity documents')
    } else {
        defaultRecs.push('<strong>Continued monitoring</strong> - Maintain standard surveillance procedures')
        defaultRecs.push('<strong>Periodic review</strong> - Schedule follow-up assessment')
    }

    if (recommendations.value?.requires_escalation) {
        defaultRecs.push('<strong>Escalation required</strong> - ' + (recommendations.value.escalation_reason || 'Senior review needed'))
    }

    return defaultRecs
})

// Chatbot state
const isChatOpen = ref(false)
const messages = ref([
    {
        id: 1,
        text: "Hello! I'm your AI investigation assistant. How can I help you with this case?",
        sender: 'bot',
        timestamp: new Date()
    }
])
const userMessage = ref('')

// Toggle chat window
const toggleChat = () => {
    isChatOpen.value = !isChatOpen.value
}

// Send message
const sendMessage = () => {
    if (!userMessage.value.trim()) return

    // Add user message
    messages.value.push({
        id: messages.value.length + 1,
        text: userMessage.value,
        sender: 'user',
        timestamp: new Date()
    })

    const userText = userMessage.value
    userMessage.value = ''

    // Generate response using actual data
    setTimeout(() => {
        const botResponse = generateBotResponse(userText)
        messages.value.push({
            id: messages.value.length + 1,
            text: botResponse,
            sender: 'bot',
            timestamp: new Date()
        })
    }, 800)
}

// Generate bot response using actual case data
const generateBotResponse = (userText) => {
    const text = userText.toLowerCase()
    const rd = riskDecomposition.value
    const ctx = caseContext.value
    const na = networkAnalysis.value
    const recs = recommendations.value

    if (text.includes('risk') || text.includes('score')) {
        return `This case has a risk score of ${rd?.overall_risk_score || ctx?.case_info?.case_score || 'N/A'}/100, classified as ${rd?.risk_level || 'Unknown'}. ${rd?.key_differentiators?.[0] || ''}`
    } else if (text.includes('evidence') || text.includes('proof')) {
        const alerts = ctx?.alerts || []
        const evidence = alerts.flatMap(a => a.evidence?.map(e => e.explanation) || []).slice(0, 3)
        return `Key evidence includes: ${evidence.join('; ') || 'No evidence data available.'}`
    } else if (text.includes('recommend') || text.includes('action')) {
        const actions = recs?.recommendations?.slice(0, 3).map(r => r.action).join('; ') || 'No recommendations available.'
        return `Recommended actions: ${actions}${recs?.requires_escalation ? ' NOTE: Escalation is required.' : ''}`
    } else if (text.includes('network') || text.includes('linked')) {
        return `Network analysis found ${na?.entities?.length || 0} connected entities and ${na?.clusters?.length || 0} clusters. ${na?.risk_summary?.fraud_ring_detected ? 'A fraud ring pattern was detected.' : 'No fraud ring detected.'}`
    } else if (text.includes('hello') || text.includes('hi')) {
        return `Hello! I can help you understand this fraud case. Ask me about risk scores, evidence, recommendations, or network connections.`
    } else {
        return `I can help you with information about this case's risk assessment, evidence, recommended actions, or network connections. What would you like to know?`
    }
}

// Handle Enter key
const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        sendMessage()
    }
}
</script>
