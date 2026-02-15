/**
 * API composable for SENTINEL frontend
 * Handles all communication with the Django backend
 */
export const useApi = () => {
  const baseUrl = 'http://localhost:8000/api'

  /**
   * Get all cases for the cases list page
   * @returns {Promise<Array>} List of cases
   */
  const getCases = async () => {
    const response = await fetch(`${baseUrl}/cases/`)

    if (!response.ok) {
      throw new Error(`Failed to fetch cases: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Send a message to SENTINEL chat agent
   * @param {string} caseId - The case ID (e.g., 'CASE-2025-88412')
   * @param {string} message - User's message
   * @param {Array} history - Conversation history [{role: 'user'|'assistant', content: string}]
   * @returns {Promise<{response: string, suggested_questions: string[]}>}
   */
  const chatWithSentinel = async (caseId, message, history = []) => {
    const response = await fetch(`${baseUrl}/cases/${caseId}/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.error || `API error: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Get case details
   * @param {string} caseId - The case ID
   * @returns {Promise<Object>} Case data
   */
  const getCaseData = async (caseId) => {
    const response = await fetch(`${baseUrl}/cases/${caseId}/`)

    if (!response.ok) {
      throw new Error(`Failed to fetch case: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Get case transactions
   * @param {string} caseId - The case ID
   * @returns {Promise<Array>} Transaction list
   */
  const getCaseTransactions = async (caseId) => {
    const response = await fetch(`${baseUrl}/cases/${caseId}/transactions/`)

    if (!response.ok) {
      throw new Error(`Failed to fetch transactions: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Get case logins
   * @param {string} caseId - The case ID
   * @returns {Promise<Array>} Login list
   */
  const getCaseLogins = async (caseId) => {
    const response = await fetch(`${baseUrl}/cases/${caseId}/logins/`)

    if (!response.ok) {
      throw new Error(`Failed to fetch logins: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Get case network connections
   * @param {string} caseId - The case ID
   * @returns {Promise<Array>} Network connections
   */
  const getCaseNetwork = async (caseId) => {
    const response = await fetch(`${baseUrl}/cases/${caseId}/network/`)

    if (!response.ok) {
      throw new Error(`Failed to fetch network: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Get case network graph data for visualization
   * @param {string} caseId - The case ID
   * @returns {Promise<Object>} Network graph with nodes and edges
   */
  const getCaseNetworkGraph = async (caseId) => {
    const response = await fetch(`${baseUrl}/cases/${caseId}/network-graph/`)

    if (!response.ok) {
      throw new Error(`Failed to fetch network graph: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Get customer KYC data
   * @param {string} caseId - The case ID
   * @returns {Promise<Object>} Customer data
   */
  const getCaseCustomer = async (caseId) => {
    const response = await fetch(`${baseUrl}/cases/${caseId}/customer/`)

    if (!response.ok) {
      throw new Error(`Failed to fetch customer: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Get case status/aggregations
   * @param {string} caseId - The case ID
   * @returns {Promise<Object>} Status aggregations
   */
  const getCaseStatus = async (caseId) => {
    const response = await fetch(`${baseUrl}/cases/${caseId}/status/`)

    if (!response.ok) {
      throw new Error(`Failed to fetch status: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Fetch all investigate page data in parallel
   * @param {string} caseId - The case ID
   * @returns {Promise<Object>} All case data for investigate page
   */
  const getInvestigateData = async (caseId) => {
    const [caseData, transactions, logins, network, customer, status] = await Promise.all([
      getCaseData(caseId),
      getCaseTransactions(caseId),
      getCaseLogins(caseId),
      getCaseNetwork(caseId),
      getCaseCustomer(caseId),
      getCaseStatus(caseId)
    ])

    return {
      caseData,
      transactions,
      logins,
      network,
      customer,
      status
    }
  }

  return {
    getCases,
    chatWithSentinel,
    getCaseData,
    getCaseTransactions,
    getCaseLogins,
    getCaseNetwork,
    getCaseNetworkGraph,
    getCaseCustomer,
    getCaseStatus,
    getInvestigateData
  }
}
