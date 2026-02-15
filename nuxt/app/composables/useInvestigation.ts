/**
 * Composable for fetching and managing investigation data
 * Calls POST /api/cases/{case_id}/investigate/ to get full investigation results
 */

// Type definitions matching the Django API response
export interface Evidence {
  risk_category: string
  feature: string
  impact: string
  contribution: number
  value?: number
  explanation: string
}

export interface AlertInfo {
  alert_id: string
  event_time: string
  txn_id: string
  user_id: string
  is_anomaly: number
  detector_type: string
  signal: string
  severity: string
  confidence: string
  evidence: Evidence[]
}

export interface Profile {
  user_id: string
  username: string
  created_at: string
  account_status: string
  account: {
    account_id: string
    account_status: string
    account_deposit: string
  }
  kyc: {
    kyc_level: string
    verified_at: string
    nationality: string
    residence_country: string
    age: string
    occupation: string
    income: string
    source_of_funds: string
  }
  risk: {
    risk_tier: string
    pep_flag: boolean
    sanctions_status: string
    adverse_media_flag: boolean
  }
  verification: {
    email_verified: boolean
    phone_verified: boolean
  }
}

export interface CaseInfo {
  case_id: string
  user_id: string
  status: string
  opened_at: string
  last_updated: string
  case_score: number
  risk_level: string
}

export interface CaseContext {
  case_id: string
  user_id: string
  assembled_at: string
  case_info: CaseInfo
  profile: Profile
  transactions: any[]
  logins: any[]
  network_events: any[]
  status: any
  alerts: AlertInfo[]
  data_completeness: {
    case_data: boolean
    profile: boolean
    transactions: boolean
    logins: boolean
    network_events: boolean
    status: boolean
    alerts: boolean
  }
}

export interface RiskComponent {
  component_name: string
  component_score: number
  weight: number
  weighted_contribution: number
  explanation: string
  contributing_factors: string[]
}

export interface RiskDecomposition {
  overall_risk_score: number
  risk_level: string
  components: RiskComponent[]
  comparison_baseline: string
  key_differentiators: string[]
}

export interface TimelineEvent {
  t: string
  type: string
  event: string
  details: Record<string, any>
  related_alerts: string[]
  severity: string
}

export interface Timeline {
  sequence: TimelineEvent[]
  escalation_assessment: {
    pattern: string
    severity: string
    escalation_detected: boolean
    time_to_escalation_minutes?: number
    narrative?: string
  }
  window_start: string
  window_end: string
  total_events: number
  critical_events: number
}

export interface NetworkEntity {
  entity_id: string
  entity_type: string
  risk_level: string
  attributes: Record<string, any>
}

export interface NetworkCluster {
  cluster_id: string
  entities: string[]
  risk_score: number
  classification: string
  central_entity: string
}

export interface NetworkAnalysis {
  entities: NetworkEntity[]
  edges: any[]
  clusters: NetworkCluster[]
  risk_summary: Record<string, any>
  recommended_investigations: string[]
}

export interface ReportSection {
  title: string
  content: string
  subsections?: { title: string; content: string }[]
}

export interface CaseReport {
  report_id: string
  case_id: string
  generated_at: string
  report_type: string
  executive_summary: string
  sections: ReportSection[]
  key_findings: string[]
  recommendations: string[]
  appendices: any[]
}

export interface Recommendation {
  action: string
  priority: string
  rationale: string
  estimated_effort: string
}

export interface Recommendations {
  recommendations: Recommendation[]
  requires_escalation: boolean
  escalation_reason?: string
}

export interface InvestigationResult {
  case_id: string
  investigation_id: string
  started_at: string
  completed_at: string
  status: string
  case_context: CaseContext
  explainability: {
    primary_hypothesis: string
    confidence: number
    justification: any[]
  }
  risk_decomposition: RiskDecomposition
  pattern_matches: {
    top_matches: any[]
    fraud_type_probabilities: Record<string, number>
  }
  timeline: Timeline
  recommendations: Recommendations
  network_analysis: NetworkAnalysis
  report: CaseReport
  skills_executed: any[]
  total_duration_ms: number
  dashboard_summary: {
    headline: string
    risk_level: string
    risk_score: number
    key_evidence: string[]
    recommended_actions: any[]
    escalation_required: boolean
  }
}

export function useInvestigation(caseId: Ref<string> | string) {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://127.0.0.1:8000'

  const data = ref<InvestigationResult | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchInvestigation = async (options?: {
    includeReport?: boolean
    includeRegulatory?: boolean
  }) => {
    const id = unref(caseId)
    if (!id) {
      error.value = 'No case ID provided'
      return
    }

    loading.value = true
    error.value = null

    try {
      const response = await $fetch<InvestigationResult>(
        `${apiBase}/api/cases/${id}/investigate/`,
        {
          method: 'POST',
          body: {
            include_report: options?.includeReport ?? true,
            include_regulatory: options?.includeRegulatory ?? false
          }
        }
      )
      data.value = response
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch investigation data'
      console.error('Investigation fetch error:', e)
    } finally {
      loading.value = false
    }
  }

  // Computed helpers for easy access
  const caseContext = computed(() => data.value?.case_context)
  const profile = computed(() => data.value?.case_context?.profile)
  const riskDecomposition = computed(() => data.value?.risk_decomposition)
  const timeline = computed(() => data.value?.timeline)
  const networkAnalysis = computed(() => data.value?.network_analysis)
  const report = computed(() => data.value?.report)
  const recommendations = computed(() => data.value?.recommendations)
  const dashboardSummary = computed(() => data.value?.dashboard_summary)

  // Risk level styling helper
  const riskLevelClass = computed(() => {
    const level = (riskDecomposition.value?.risk_level || caseContext.value?.case_info?.risk_level || '').toLowerCase()
    switch (level) {
      case 'critical': return 'text-risk-critical'
      case 'high': return 'text-risk-high'
      case 'medium': return 'text-yellow-600'
      case 'low': return 'text-green-600'
      default: return 'text-slate-600'
    }
  })

  const riskLevelBgClass = computed(() => {
    const level = (riskDecomposition.value?.risk_level || caseContext.value?.case_info?.risk_level || '').toLowerCase()
    switch (level) {
      case 'critical': return 'bg-red-50 border-risk-critical'
      case 'high': return 'bg-orange-50 border-risk-high'
      case 'medium': return 'bg-yellow-50 border-yellow-500'
      case 'low': return 'bg-green-50 border-green-500'
      default: return 'bg-gray-50 border-gray-300'
    }
  })

  return {
    data,
    loading,
    error,
    fetchInvestigation,
    // Computed accessors
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
  }
}
