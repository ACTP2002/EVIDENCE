/**
 * API composable for SENTINEL frontend
 * Handles all communication with the Django backend
 */
export const useApi = () => {
  const baseUrl = 'http://localhost:8000/api'

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

  return {
    chatWithSentinel,
    getCaseData,
    getCaseTransactions,
    getCaseLogins,
    getCaseNetwork,
    getCaseCustomer
  }
}
