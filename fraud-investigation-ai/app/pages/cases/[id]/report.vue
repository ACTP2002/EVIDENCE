<!-- cases/[id]/report.vue -->

<template>
    <div class="min-h-screen bg-gray-50">
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
                        <p class="text-[13px] text-slate-500 font-mono">Case {{ caseId }} • Generated Feb 7, 2026</p>
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
                                <div class="text-[22px] font-bold text-slate-900 mb-1">FraudShield Investigation
                                    Platform</div>
                                <div class="text-[13px] text-slate-400 uppercase tracking-wider font-semibold">
                                    Compliance & Risk Management Division</div>
                            </div>
                        </div>

                        <div class="grid grid-cols-3 gap-5">
                            <div>
                                <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Report
                                    Type</div>
                                <div class="text-sm text-slate-900 font-semibold">Fraud Investigation Summary</div>
                            </div>
                            <div>
                                <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Case ID
                                </div>
                                <div class="text-sm text-slate-900 font-semibold font-mono">{{ caseId }}</div>
                            </div>
                            <div>
                                <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">
                                    Generated</div>
                                <div class="text-sm text-slate-900 font-semibold">February 7, 2026 14:32 UTC</div>
                            </div>
                            <div>
                                <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">
                                    Investigator</div>
                                <div class="text-sm text-slate-900 font-semibold">Sarah Johnson (SJ-19284)</div>
                            </div>
                            <div>
                                <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">
                                    Classification</div>
                                <div class="text-sm text-risk-high font-bold">CONFIDENTIAL</div>
                            </div>
                            <div>
                                <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Status
                                </div>
                                <div class="text-sm text-risk-critical font-bold">CONFIRMED FRAUD</div>
                            </div>
                        </div>
                    </div>

                    <!-- Executive Summary -->
                    <section class="mb-12">
                        <h2 class="text-xl font-bold text-slate-900 mb-6 pb-3 border-b-2 border-gray-100">Executive
                            Summary</h2>

                        <div class="flex items-start gap-4 p-5 bg-red-50 border-2 border-risk-critical rounded-lg mb-6">
                            <div
                                class="w-12 h-12 rounded-lg bg-risk-critical text-white flex items-center justify-center flex-shrink-0">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                    <path d="M12 8V12M12 16V16.5" stroke="currentColor" stroke-width="2.5"
                                        stroke-linecap="round" />
                                    <path d="M3 18L12 4L21 18H3Z" stroke="currentColor" stroke-width="2"
                                        stroke-linejoin="round" />
                                </svg>
                            </div>
                            <div>
                                <div class="text-base font-bold text-risk-critical font-mono mb-1">CRITICAL RISK LEVEL -
                                    RISK SCORE: 94/100</div>
                                <div class="text-sm text-slate-600">Multiple high-confidence fraud indicators detected
                                </div>
                            </div>
                        </div>

                        <p class="text-sm leading-relaxed text-slate-900 mb-4">
                            This report documents the investigation of client Marcus Chen (Client ID: CL-48291) for
                            suspected money laundering activity. The investigation was initiated on February 7, 2026,
                            following automated detection of critical risk indicators by the FraudShield AI monitoring
                            system.
                        </p>

                        <p class="text-sm leading-relaxed text-slate-900 mb-4">
                            The subject account exhibits multiple high-severity fraud indicators with a composite risk
                            score of 94/100, placing it in the Critical risk category. Primary concerns include: (1)
                            financial activity grossly inconsistent with declared income profile, (2) systematic use of
                            virtual private networks to access the platform from sanctioned jurisdictions, and (3)
                            transaction patterns matching confirmed money laundering cases with 92% confidence.
                        </p>

                        <p class="text-sm leading-relaxed text-slate-900">
                            <strong>Recommended Action:</strong> Immediate account suspension, asset freeze, and
                            referral to financial crimes enforcement authorities. Evidence suggests coordinated fraud
                            network activity involving multiple linked accounts.
                        </p>
                    </section>

                    <!-- Subject Information -->
                    <section class="mb-12">
                        <h2 class="text-xl font-bold text-slate-900 mb-6 pb-3 border-b-2 border-gray-100">Subject
                            Information</h2>

                        <div class="space-y-4">
                            <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                <div class="text-[13px] font-semibold text-slate-400">Full Name</div>
                                <div class="text-sm text-slate-900">Marcus Chen</div>
                            </div>
                            <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                <div class="text-[13px] font-semibold text-slate-400">Client ID</div>
                                <div class="text-sm text-slate-900 font-mono">CL-48291</div>
                            </div>
                            <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                <div class="text-[13px] font-semibold text-slate-400">Account Created</div>
                                <div class="text-sm text-slate-900">January 15, 2024</div>
                            </div>
                            <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                <div class="text-[13px] font-semibold text-slate-400">Account Status</div>
                                <div class="text-sm text-status-open font-semibold">Active (Under Investigation)</div>
                            </div>
                            <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                <div class="text-[13px] font-semibold text-slate-400">Declared Occupation</div>
                                <div class="text-sm text-slate-900">Student</div>
                            </div>
                            <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                <div class="text-[13px] font-semibold text-slate-400">Declared Monthly Income</div>
                                <div class="text-sm text-slate-900">$5,000 USD</div>
                            </div>
                            <div class="grid grid-cols-[220px_1fr] gap-5 pb-4 border-b border-gray-100">
                                <div class="text-[13px] font-semibold text-slate-400">Registered Address</div>
                                <div class="text-sm text-slate-900">742 Evergreen Terrace, Springfield, IL 62701</div>
                            </div>
                            <div class="grid grid-cols-[220px_1fr] gap-5">
                                <div class="text-[13px] font-semibold text-slate-400">Email</div>
                                <div class="text-sm text-slate-900 font-mono">m.chen.2024@tempmail-xyz.com</div>
                            </div>
                        </div>
                    </section>

                    <!-- Risk Indicators -->
                    <section class="mb-12">
                        <h2 class="text-xl font-bold text-slate-900 mb-6 pb-3 border-b-2 border-gray-100">Risk
                            Indicators Analysis</h2>

                        <!-- Critical Indicator 1 -->
                        <div class="border-l-4 border-risk-critical bg-red-50 p-6 rounded-r-lg mb-8">
                            <div class="flex justify-between items-center mb-4">
                                <div class="text-[11px] uppercase tracking-wider text-risk-critical font-bold">CRITICAL
                                    SEVERITY</div>
                                <div class="text-xs font-mono font-semibold text-slate-400">Risk Impact: +42 points
                                </div>
                            </div>
                            <h3 class="text-base font-bold text-slate-900 mb-4">Financial Activity Inconsistent with
                                Customer Profile</h3>
                            <p class="text-sm leading-relaxed text-slate-900 mb-5">
                                Subject declared monthly income of $5,000 USD during account registration with stated
                                occupation as "Student." However, account activity over the past 30 days shows total
                                deposits of $71,000 USD, representing a 1,420% deviation from declared income capacity.
                            </p>
                            <div class="bg-white p-4 rounded-lg mb-5">
                                <div class="text-[13px] font-bold text-slate-900 mb-3">Supporting Evidence:</div>
                                <ul class="list-inside list-disc space-y-1.5">
                                    <li class="text-[13px] leading-relaxed text-slate-600">Total deposits (30-day
                                        period): $71,000 USD</li>
                                    <li class="text-[13px] leading-relaxed text-slate-600">Average transaction size:
                                        $8,500 USD</li>
                                    <li class="text-[13px] leading-relaxed text-slate-600">Largest single deposit:
                                        $24,000 USD (Feb 5, 2026)</li>
                                    <li class="text-[13px] leading-relaxed text-slate-600">Number of deposit
                                        transactions: 18</li>
                                    <li class="text-[13px] leading-relaxed text-slate-600">Income deviation ratio:
                                        14.2:1</li>
                                </ul>
                            </div>
                            <p class="text-sm leading-relaxed text-slate-900">
                                <strong>Assessment:</strong> The magnitude of this discrepancy cannot be explained by
                                legitimate income sources consistent with the declared occupation. Pattern is consistent
                                with money laundering activity where illicit funds are introduced into the financial
                                system through structuring and layering techniques.
                            </p>
                        </div>

                        <!-- Critical Indicator 2 -->
                        <div class="border-l-4 border-risk-critical bg-red-50 p-6 rounded-r-lg mb-8">
                            <div class="flex justify-between items-center mb-4">
                                <div class="text-[11px] uppercase tracking-wider text-risk-critical font-bold">CRITICAL
                                    SEVERITY</div>
                                <div class="text-xs font-mono font-semibold text-slate-400">Risk Impact: +38 points
                                </div>
                            </div>
                            <h3 class="text-base font-bold text-slate-900 mb-4">VPN Access from Sanctioned Jurisdictions
                            </h3>
                            <p class="text-sm leading-relaxed text-slate-900 mb-5">
                                Analysis of login activity reveals systematic use of virtual private network (VPN)
                                services to obfuscate geographic location. 73% of all login sessions (87 of 119 total
                                sessions) originated from IP addresses traced to sanctioned jurisdictions, in violation
                                of platform terms of service and applicable sanctions regulations.
                            </p>
                            <div class="bg-white p-4 rounded-lg mb-5">
                                <div class="text-[13px] font-bold text-slate-900 mb-3">Geographic Access Pattern:</div>
                                <ul class="list-inside list-disc space-y-1.5">
                                    <li class="text-[13px] leading-relaxed text-slate-600">VPN usage rate: 73% of all
                                        sessions</li>
                                    <li class="text-[13px] leading-relaxed text-slate-600">Sanctioned jurisdiction
                                        access: 87 sessions</li>
                                    <li class="text-[13px] leading-relaxed text-slate-600">Peak activity hours: 2:00 AM
                                        - 5:00 AM (subject's registered timezone)</li>
                                    <li class="text-[13px] leading-relaxed text-slate-600">Known VPN services detected:
                                        5 different providers</li>
                                    <li class="text-[13px] leading-relaxed text-slate-600">IP addresses rotated: 34
                                        unique IPs across 87 sessions</li>
                                </ul>
                            </div>
                            <p class="text-sm leading-relaxed text-slate-900">
                                <strong>Assessment:</strong> Deliberate and sophisticated evasion of geographic
                                restrictions suggests knowledge of regulatory violations and intent to conceal
                                sanctioned jurisdiction activity. Access timing (unusual hours) further supports
                                coordinated fraud operation hypothesis.
                            </p>
                        </div>

                        <!-- High Indicator -->
                        <div class="border-l-4 border-risk-high bg-orange-50 p-6 rounded-r-lg">
                            <div class="flex justify-between items-center mb-4">
                                <div class="text-[11px] uppercase tracking-wider text-risk-high font-bold">HIGH SEVERITY
                                </div>
                                <div class="text-xs font-mono font-semibold text-slate-400">Risk Impact: +14 points
                                </div>
                            </div>
                            <h3 class="text-base font-bold text-slate-900 mb-4">Transaction Pattern Matches Known Money
                                Laundering Networks</h3>
                            <p class="text-sm leading-relaxed text-slate-900 mb-5">
                                AI pattern recognition system identified behavioral signatures matching 12 confirmed
                                money laundering cases from Q4 2025 with 92% confidence score. Subject's transaction
                                sequence exhibits rapid deposit-withdrawal cycles characteristic of "layering" phase
                                money laundering operations.
                            </p>
                            <div class="bg-white p-4 rounded-lg">
                                <div class="text-[13px] font-bold text-slate-900 mb-3">Pattern Analysis:</div>
                                <ul class="list-inside list-disc space-y-1.5">
                                    <li class="text-[13px] leading-relaxed text-slate-600">Pattern match confidence: 92%
                                    </li>
                                    <li class="text-[13px] leading-relaxed text-slate-600">Confirmed similar cases: 12
                                        (Q4 2025)</li>
                                    <li class="text-[13px] leading-relaxed text-slate-600">Average cycle duration: 47
                                        minutes (deposit to withdrawal)</li>
                                    <li class="text-[13px] leading-relaxed text-slate-600">Withdrawal rate: 94% of
                                        deposited funds within 72 hours</li>
                                    <li class="text-[13px] leading-relaxed text-slate-600">Intermediate account
                                        transfers: 8 transactions to unknown recipients</li>
                                </ul>
                            </div>
                        </div>
                    </section>

                    <!-- Timeline -->
                    <section class="mb-12">
                        <h2 class="text-xl font-bold text-slate-900 mb-6 pb-3 border-b-2 border-gray-100">Investigation
                            Timeline</h2>

                        <div class="space-y-7">
                            <div class="relative pl-7">
                                <div
                                    class="absolute left-0 top-1 w-4 h-4 rounded-full bg-accent border-[3px] border-white shadow-[0_0_0_2px_#E4E7EB]">
                                </div>
                                <div class="absolute left-[7px] top-5 bottom-[-28px] w-0.5 bg-gray-200"></div>
                                <div class="text-xs font-mono text-slate-400 mb-1.5">February 5, 2026 - 09:15 AM UTC
                                </div>
                                <div class="text-[15px] font-bold text-slate-900 mb-2">Large Deposit Transaction</div>
                                <div class="text-[13px] leading-relaxed text-slate-600">
                                    Subject deposited $24,000 USD in single transaction. Amount represents 480% of
                                    declared monthly income. Transaction flagged by automated monitoring system for
                                    review.
                                </div>
                            </div>

                            <div class="relative pl-7">
                                <div
                                    class="absolute left-0 top-1 w-4 h-4 rounded-full bg-accent border-[3px] border-white shadow-[0_0_0_2px_#E4E7EB]">
                                </div>
                                <div class="absolute left-[7px] top-5 bottom-[-28px] w-0.5 bg-gray-200"></div>
                                <div class="text-xs font-mono text-slate-400 mb-1.5">February 5, 2026 - 02:30 PM UTC
                                </div>
                                <div class="text-[15px] font-bold text-slate-900 mb-2">VPN Access Detected</div>
                                <div class="text-[13px] leading-relaxed text-slate-600">
                                    Login session initiated via VPN from IP address traced to sanctioned jurisdiction.
                                    Device fingerprint analysis shows match with 7 other flagged accounts currently
                                    under investigation.
                                </div>
                            </div>

                            <div class="relative pl-7">
                                <div
                                    class="absolute left-0 top-1 w-4 h-4 rounded-full bg-accent border-[3px] border-white shadow-[0_0_0_2px_#E4E7EB]">
                                </div>
                                <div class="absolute left-[7px] top-5 bottom-[-28px] w-0.5 bg-gray-200"></div>
                                <div class="text-xs font-mono text-slate-400 mb-1.5">February 6, 2026 - 03:45 AM UTC
                                </div>
                                <div class="text-[15px] font-bold text-slate-900 mb-2">Rapid Withdrawal Sequence</div>
                                <div class="text-[13px] leading-relaxed text-slate-600">
                                    Subject withdrew $22,500 USD across 8 separate transactions over 47-minute period.
                                    Withdrawal destinations include 5 unknown recipient accounts. Pattern consistent
                                    with money laundering "layering" techniques.
                                </div>
                            </div>

                            <div class="relative pl-7">
                                <div
                                    class="absolute left-0 top-1 w-4 h-4 rounded-full bg-accent border-[3px] border-white shadow-[0_0_0_2px_#E4E7EB]">
                                </div>
                                <div class="absolute left-[7px] top-5 bottom-[-28px] w-0.5 bg-gray-200"></div>
                                <div class="text-xs font-mono text-slate-400 mb-1.5">February 7, 2026 - 08:20 AM UTC
                                </div>
                                <div class="text-[15px] font-bold text-slate-900 mb-2">AI System Alert Generated</div>
                                <div class="text-[13px] leading-relaxed text-slate-600">
                                    FraudShield AI monitoring system generated Critical severity alert with composite
                                    risk score of 94/100. Case automatically escalated to senior investigator queue for
                                    immediate review.
                                </div>
                            </div>

                            <div class="relative pl-7">
                                <div
                                    class="absolute left-0 top-1 w-4 h-4 rounded-full bg-accent border-[3px] border-white shadow-[0_0_0_2px_#E4E7EB]">
                                </div>
                                <div class="text-xs font-mono text-slate-400 mb-1.5">February 7, 2026 - 14:32 PM UTC
                                </div>
                                <div class="text-[15px] font-bold text-slate-900 mb-2">Investigation Completed</div>
                                <div class="text-[13px] leading-relaxed text-slate-600">
                                    Senior investigator Sarah Johnson completed comprehensive case review. Evidence
                                    supports classification as Confirmed Fraud. Report generated for compliance review
                                    and regulatory reporting.
                                </div>
                            </div>
                        </div>
                    </section>

                    <!-- Network Analysis -->
                    <section class="mb-12">
                        <h2 class="text-xl font-bold text-slate-900 mb-6 pb-3 border-b-2 border-gray-100">Network
                            Analysis</h2>

                        <p class="text-sm leading-relaxed text-slate-900 mb-6">
                            Cross-account forensic analysis reveals subject account is part of larger coordinated fraud
                            network. Multiple technical and behavioral connections identified to other accounts
                            currently under investigation or previously confirmed as fraudulent.
                        </p>

                        <div class="grid grid-cols-3 gap-5 my-6">
                            <div class="p-5 bg-white border-2 border-gray-200 rounded-lg text-center">
                                <div class="text-[28px] font-bold font-mono text-risk-critical mb-2">7 Accounts</div>
                                <div class="text-[13px] font-semibold text-slate-900 mb-1.5">Shared Device Fingerprint
                                </div>
                                <div class="text-xs text-slate-400">Device ID: 7AF8-9B2C-E143-0D29</div>
                            </div>
                            <div class="p-5 bg-white border-2 border-gray-200 rounded-lg text-center">
                                <div class="text-[28px] font-bold font-mono text-risk-critical mb-2">3 Accounts</div>
                                <div class="text-[13px] font-semibold text-slate-900 mb-1.5">Shared IP Addresses</div>
                                <div class="text-xs text-slate-400">During overlapping time periods</div>
                            </div>
                            <div class="p-5 bg-white border-2 border-gray-200 rounded-lg text-center">
                                <div class="text-[28px] font-bold font-mono text-risk-critical mb-2">Coordinated</div>
                                <div class="text-[13px] font-semibold text-slate-900 mb-1.5">Transaction Timing</div>
                                <div class="text-xs text-slate-400">±15 minute synchronization detected</div>
                            </div>
                        </div>

                        <p class="text-sm leading-relaxed text-slate-900">
                            <strong>Network Assessment:</strong> Evidence strongly suggests organized fraud operation
                            involving minimum 10-15 controlled accounts operating in coordination. Recommend expanding
                            investigation to all linked accounts and implementing coordinated enforcement action.
                        </p>
                    </section>

                    <!-- Conclusions -->
                    <section class="mb-12">
                        <h2 class="text-xl font-bold text-slate-900 mb-6 pb-3 border-b-2 border-gray-100">Conclusions &
                            Recommendations</h2>

                        <div class="mb-8">
                            <h3 class="text-base font-bold text-slate-900 mb-4">Findings</h3>
                            <ol class="list-decimal list-inside space-y-3">
                                <li class="text-sm leading-relaxed text-slate-900">Subject account exhibits multiple
                                    critical-severity fraud indicators with composite risk score of 94/100, exceeding
                                    threshold for confirmed fraud classification.</li>
                                <li class="text-sm leading-relaxed text-slate-900">Financial activity is grossly
                                    inconsistent with declared customer profile, showing deviation of 1,420% from stated
                                    income capacity.</li>
                                <li class="text-sm leading-relaxed text-slate-900">Systematic VPN usage to access
                                    platform from sanctioned jurisdictions demonstrates deliberate regulatory evasion.
                                </li>
                                <li class="text-sm leading-relaxed text-slate-900">Transaction patterns match known
                                    money laundering techniques with 92% confidence based on AI pattern analysis.</li>
                                <li class="text-sm leading-relaxed text-slate-900">Account is part of larger coordinated
                                    fraud network with multiple technical and behavioral connections to other suspicious
                                    accounts.</li>
                            </ol>
                        </div>

                        <div>
                            <h3 class="text-base font-bold text-slate-900 mb-4">Recommended Actions</h3>
                            <ol class="list-decimal list-inside space-y-3">
                                <li class="text-sm leading-relaxed text-slate-900"><strong>Immediate account
                                        suspension</strong> - Prevent further fraudulent transactions</li>
                                <li class="text-sm leading-relaxed text-slate-900"><strong>Asset freeze</strong> -
                                    Preserve evidence and prevent dissipation of funds</li>
                                <li class="text-sm leading-relaxed text-slate-900"><strong>Regulatory reporting</strong>
                                    - File Suspicious Activity Report (SAR) with FinCEN</li>
                                <li class="text-sm leading-relaxed text-slate-900"><strong>Law enforcement
                                        referral</strong> - Coordinate with financial crimes task force</li>
                                <li class="text-sm leading-relaxed text-slate-900"><strong>Network investigation
                                        expansion</strong> - Investigate all identified linked accounts</li>
                                <li class="text-sm leading-relaxed text-slate-900"><strong>Customer verification
                                        re-check</strong> - Enhanced due diligence on identity documents</li>
                            </ol>
                        </div>
                    </section>

                    <!-- Footer -->
                    <div class="pt-6 mt-12">
                        <div class="h-0.5 bg-primary mb-5"></div>
                        <div class="grid grid-cols-3 gap-5 mb-4">
                            <div>
                                <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">
                                    Generated by</div>
                                <div class="text-xs text-slate-600 font-semibold">FraudShield AI Investigation Platform
                                    v4.2</div>
                            </div>
                            <div>
                                <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Report
                                    ID</div>
                                <div class="text-xs text-slate-600 font-semibold font-mono">RPT-2024-0847-A1</div>
                            </div>
                            <div>
                                <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">Page
                                </div>
                                <div class="text-xs text-slate-600 font-semibold">1 of 1</div>
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
    </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const caseId = computed(() => route.params.id || 'FR-2024-0847')

// In a real app, you would fetch case data based on caseId
// For now, we'll use the caseId dynamically in the template
</script>