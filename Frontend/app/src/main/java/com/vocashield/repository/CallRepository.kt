package com.vocashield.repository

import android.content.Context
import com.vocashield.models.CallAnalysis
import com.vocashield.models.RiskLevel
import com.vocashield.models.RiskSignal
import com.vocashield.models.TrustedContact
import com.vocashield.network.WebSocketManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

interface CallRepository {
    val liveCallState: StateFlow<CallAnalysis?>
    val recentCallsState: StateFlow<List<CallAnalysis>>
    val trustedContactsState: StateFlow<List<TrustedContact>>
    val isProtectionEnabled: StateFlow<Boolean>
    val riskThreshold: StateFlow<Int>

    fun startLiveCallSimulation()
    fun stopLiveCallSimulation()
    fun resetSimulation()
    fun addTrustedContact(contact: TrustedContact)
    fun removeTrustedContact(contactId: String)
    fun setProtectionEnabled(enabled: Boolean)
    fun setRiskThreshold(threshold: Int)
}

class MockCallRepository(
    private val context: Context,
    private val backendUrl: String = "10.0.2.2:8000"  // Default: Android emulator → localhost
) : CallRepository {

    private val scope = CoroutineScope(Dispatchers.Default)
    private var collectJob: Job? = null

    // Real WebSocket manager
    private val wsManager = WebSocketManager(context)

    private val _liveCallState = MutableStateFlow<CallAnalysis?>(null)
    override val liveCallState: StateFlow<CallAnalysis?> = _liveCallState.asStateFlow()

    private val _recentCallsState = MutableStateFlow<List<CallAnalysis>>(
        listOf(
            CallAnalysis(
                callId = "call_1",
                callerName = "Mom",
                callerNumber = "+91 98765 11111",
                durationSeconds = 142,
                overallRiskScore = 12,
                voiceRiskScore = 10,
                scamRiskScore = 15,
                identityRiskScore = 5,
                detectedSignals = emptyList(),
                timestamp = "10:42 AM",
                isLive = false
            ),
            CallAnalysis(
                callId = "call_2",
                callerName = "Alex (Friend)",
                callerNumber = "+91 98765 22222",
                durationSeconds = 95,
                overallRiskScore = 18,
                voiceRiskScore = 15,
                scamRiskScore = 20,
                identityRiskScore = 10,
                detectedSignals = emptyList(),
                timestamp = "09:31 AM",
                isLive = false
            ),
            CallAnalysis(
                callId = "call_3",
                callerName = "Unknown Caller",
                callerNumber = "+91 98765 99999",
                durationSeconds = 48,
                overallRiskScore = 87,
                voiceRiskScore = 82,
                scamRiskScore = 91,
                identityRiskScore = 72,
                claimedIdentity = "Brother",
                detectedSignals = listOf(
                    RiskSignal("Synthetic voice characteristics", "AASIST spectral mismatch detected", RiskLevel.CRITICAL),
                    RiskSignal("Urgency detected", "High speech velocity & urgent keywords", RiskLevel.HIGH),
                    RiskSignal("Financial request", "Requesting bank transfer to unknown account", RiskLevel.CRITICAL),
                    RiskSignal("Caller identity unverified", "Number not found in trusted contacts", RiskLevel.MEDIUM)
                ),
                riskHistory = listOf(15, 32, 51, 72, 87),
                timestamp = "08:15 AM",
                isLive = false
            )
        )
    )
    override val recentCallsState: StateFlow<List<CallAnalysis>> = _recentCallsState.asStateFlow()

    private val _trustedContactsState = MutableStateFlow<List<TrustedContact>>(
        listOf(
            TrustedContact(
                id = "tc_1",
                name = "Mom",
                relationship = "Mother",
                phoneNumber = "+91 98765 11111",
                verificationQuestion = "What is the name of our family pet?",
                expectedAnswer = "Bruno"
            ),
            TrustedContact(
                id = "tc_2",
                name = "Rahul",
                relationship = "Brother",
                phoneNumber = "+91 98765 33333",
                verificationQuestion = "Where did we go on vacation in 2022?",
                expectedAnswer = "Goa"
            )
        )
    )
    override val trustedContactsState: StateFlow<List<TrustedContact>> = _trustedContactsState.asStateFlow()

    private val _isProtectionEnabled = MutableStateFlow(true)
    override val isProtectionEnabled: StateFlow<Boolean> = _isProtectionEnabled.asStateFlow()

    private val _riskThreshold = MutableStateFlow(80)
    override val riskThreshold: StateFlow<Int> = _riskThreshold.asStateFlow()

    // ─── LIVE MIC DETECTION ──────────────────────────────────────────────────

    override fun startLiveCallSimulation() {
        collectJob?.cancel()

        // Connect to the backend WebSocket
        wsManager.connect(wsUrl = backendUrl, callerNumber = "+91 00000 00000")

        // Collect real-time state from the WebSocket manager into our state flow
        collectJob = scope.launch {
            wsManager.liveCallState.collect { analysis ->
                _liveCallState.value = analysis
            }
        }
    }

    override fun stopLiveCallSimulation() {
        wsManager.disconnect()
        collectJob?.cancel()

        val currentCall = _liveCallState.value
        if (currentCall != null) {
            val endedCall = currentCall.copy(isLive = false, timestamp = "Just Now")
            _recentCallsState.value = listOf(endedCall) + _recentCallsState.value
        }
        _liveCallState.value = null
    }

    override fun resetSimulation() {
        wsManager.disconnect()
        collectJob?.cancel()
        _liveCallState.value = null
    }

    override fun addTrustedContact(contact: TrustedContact) {
        _trustedContactsState.value = _trustedContactsState.value + contact
    }

    override fun removeTrustedContact(contactId: String) {
        _trustedContactsState.value = _trustedContactsState.value.filterNot { it.id == contactId }
    }

    override fun setProtectionEnabled(enabled: Boolean) {
        _isProtectionEnabled.value = enabled
    }

    override fun setRiskThreshold(threshold: Int) {
        _riskThreshold.value = threshold
    }
}
