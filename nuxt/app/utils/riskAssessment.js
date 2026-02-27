/**
 * Risk Assessment Utilities
 * 
 * These utilities help calculate and format risk levels dynamically
 * based on risk scores throughout the fraud investigation platform.
 */

/**
 * Calculate risk level from a numeric risk score
 * 
 * @param {number} score - Risk score (0-100)
 * @returns {string} Risk level: 'Critical', 'High', 'Medium', or 'Low'
 * 
 * Thresholds:
 * - Critical: 80-100
 * - High: 60-79
 * - Medium: 40-59
 * - Low: 0-39
 */
export const getRiskLevel = (score) => {
  if (score >= 90) return 'Critical'
  if (score >= 60) return 'High'
  if (score >= 40) return 'Medium'
  return 'Low'
}

/**
 * Get Tailwind CSS classes for risk level styling
 * 
 * @param {number} score - Risk score (0-100)
 * @returns {object} Object containing text and background color classes
 */
export const getRiskClasses = (score) => {
  const level = getRiskLevel(score)
  
  const classMap = {
    Critical: {
      text: 'text-risk-critical',
      bg: 'bg-risk-critical',
      badgeBg: 'bg-red-50',
      badgeText: 'text-risk-critical'
    },
    High: {
      text: 'text-risk-high',
      bg: 'bg-risk-high',
      badgeBg: 'bg-orange-50',
      badgeText: 'text-risk-high'
    },
    Medium: {
      text: 'text-risk-medium',
      bg: 'bg-risk-medium',
      badgeBg: 'bg-amber-50',
      badgeText: 'text-risk-medium'
    },
    Low: {
      text: 'text-risk-low',
      bg: 'bg-risk-low',
      badgeBg: 'bg-green-50',
      badgeText: 'text-risk-low'
    }
  }
  
  return classMap[level]
}

/**
 * Get color hex code for risk level (for charts/visualizations)
 * 
 * @param {number} score - Risk score (0-100)
 * @returns {string} Hex color code
 */
export const getRiskColor = (score) => {
  const level = getRiskLevel(score)
  
  const colorMap = {
    Critical: '#DC2626',
    High: '#EA580C',
    Medium: '#F59E0B',
    Low: '#10B981'
  }
  
  return colorMap[level]
}

/**
 * Format risk score with level indicator
 * 
 * @param {number} score - Risk score (0-100)
 * @returns {string} Formatted string like "94 (Critical)"
 */
export const formatRiskScore = (score) => {
  const level = getRiskLevel(score)
  return `${score} (${level})`
}

/**
 * Check if a case should be prioritized based on risk score
 * 
 * @param {number} score - Risk score (0-100)
 * @returns {boolean} True if score is Critical or High
 */
export const isPriority = (score) => {
  const level = getRiskLevel(score)
  return level === 'Critical' || level === 'High'
}

/**
 * Get risk level statistics from an array of cases
 * 
 * @param {Array} cases - Array of case objects with riskScore property
 * @returns {object} Statistics object with counts for each level
 */
export const getRiskStatistics = (cases) => {
  const stats = {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    total: cases.length
  }
  
  cases.forEach(case_ => {
    const level = getRiskLevel(case_.riskScore).toLowerCase()
    stats[level]++
  })
  
  return stats
}