package com.vocashield.models

enum class RiskLevel {
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL
}

data class RiskSignal(
    val title: String,
    val description: String = "",
    val severity: RiskLevel = RiskLevel.HIGH,
    val iconName: String = "Warning"
)

data class CallAnalysis(
    val callId: String,
    val callerName: String,
    val callerNumber: String,
    val durationSeconds: Int = 0,
    val overallRiskScore: Int = 0, // 0 - 100
    val voiceRiskScore: Int = 0,   // Voice authenticity
    val scamRiskScore: Int = 0,    // Behavioral scam intent
    val identityRiskScore: Int = 0,// Identity verification mismatch
    val detectedSignals: List<RiskSignal> = emptyList(),
    val riskHistory: List<Int> = emptyList(), // Timeline of scores e.g. [15, 32, 51, 72, 87]
    val timestamp: String = "",
    val isLive: Boolean = false,
    val claimedIdentity: String? = null
) {
    val riskLevel: RiskLevel
        get() = when {
            overallRiskScore >= 80 -> RiskLevel.CRITICAL
            overallRiskScore >= 60 -> RiskLevel.HIGH
            overallRiskScore >= 35 -> RiskLevel.MEDIUM
            else -> RiskLevel.LOW
        }
}
