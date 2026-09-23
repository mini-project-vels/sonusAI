package com.vocashield.network

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import androidx.core.content.ContextCompat
import com.vocashield.models.CallAnalysis
import com.vocashield.models.RiskLevel
import com.vocashield.models.RiskSignal
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import okio.ByteString
import okio.ByteString.Companion.toByteString
import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean

private const val TAG = "WebSocketManager"

// 16 kHz, mono, 16-bit PCM — matches backend expectation
private const val SAMPLE_RATE = 16000
private const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
private const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT

class WebSocketManager(private val context: Context) {

    private val _liveCallState = MutableStateFlow<CallAnalysis?>(null)
    val liveCallState: StateFlow<CallAnalysis?> = _liveCallState.asStateFlow()

    private val _connectionState = MutableStateFlow<ConnectionState>(ConnectionState.DISCONNECTED)
    val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()

    private var webSocket: WebSocket? = null
    private var audioRecord: AudioRecord? = null
    private var micJob: Job? = null
    private val isStreaming = AtomicBoolean(false)
    private val scope = CoroutineScope(Dispatchers.IO)
    private var sessionId: String = ""

    // Tracks accumulated risk history for display
    private val riskHistory = mutableListOf<Int>()
    private val detectedSignals = mutableListOf<RiskSignal>()
    private var durationSeconds = 0

    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(0, TimeUnit.MILLISECONDS) // No read timeout for streaming
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    fun connect(wsUrl: String, callerNumber: String = "+91 00000 00000") {
        if (_connectionState.value == ConnectionState.CONNECTED) return

        sessionId = UUID.randomUUID().toString()
        riskHistory.clear()
        detectedSignals.clear()
        durationSeconds = 0

        val fullUrl = if (wsUrl.startsWith("ws")) wsUrl else "ws://$wsUrl"
        val url = "$fullUrl/ws/call/$sessionId"
        Log.d(TAG, "Connecting to: $url")

        _connectionState.value = ConnectionState.CONNECTING

        val request = Request.Builder().url(url).build()
        webSocket = client.newWebSocket(request, object : WebSocketListener() {

            override fun onOpen(ws: WebSocket, response: Response) {
                Log.d(TAG, "WebSocket connected ✅")
                _connectionState.value = ConnectionState.CONNECTED

                // Send "start" control message with caller info
                val startMsg = JSONObject().apply {
                    put("type", "start")
                    put("caller", JSONObject().apply {
                        put("phone_number", callerNumber)
                        put("call_direction", "inbound")
                    })
                }
                ws.send(startMsg.toString())

                // Start microphone capture
                startMicCapture(ws)
            }

            override fun onMessage(ws: WebSocket, text: String) {
                handleServerMessage(text)
            }

            override fun onMessage(ws: WebSocket, bytes: ByteString) {
                // Backend sends JSON as text, this shouldn't fire
            }

            override fun onClosing(ws: WebSocket, code: Int, reason: String) {
                Log.d(TAG, "WebSocket closing: $reason")
                ws.close(1000, null)
            }

            override fun onClosed(ws: WebSocket, code: Int, reason: String) {
                Log.d(TAG, "WebSocket closed")
                _connectionState.value = ConnectionState.DISCONNECTED
                stopMicCapture()
            }

            override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
                Log.e(TAG, "WebSocket ERROR: ${t.message}")
                _connectionState.value = ConnectionState.ERROR
                stopMicCapture()
            }
        })
    }

    private fun startMicCapture(ws: WebSocket) {
        if (!hasMicPermission()) {
            Log.e(TAG, "MICROPHONE permission not granted!")
            _connectionState.value = ConnectionState.ERROR
            return
        }

        val bufferSize = AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT)
            .coerceAtLeast(3200) // At least 100ms of audio

        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.VOICE_COMMUNICATION,
            SAMPLE_RATE,
            CHANNEL_CONFIG,
            AUDIO_FORMAT,
            bufferSize * 4
        )

        isStreaming.set(true)

        micJob = scope.launch {
            val buffer = ShortArray(bufferSize)
            val byteBuffer = ByteArray(bufferSize * 2) // 2 bytes per 16-bit sample
            var durationTick = 0L

            audioRecord?.startRecording()
            Log.d(TAG, "🎙️ Microphone recording started")

            while (isStreaming.get()) {
                val samplesRead = audioRecord?.read(buffer, 0, buffer.size) ?: -1

                if (samplesRead > 0) {
                    // Convert short[] → byte[] (little-endian PCM16)
                    for (i in 0 until samplesRead) {
                        val sample = buffer[i]
                        byteBuffer[i * 2] = (sample.toInt() and 0xFF).toByte()
                        byteBuffer[i * 2 + 1] = ((sample.toInt() shr 8) and 0xFF).toByte()
                    }

                    // Send raw PCM bytes over WebSocket
                    ws.send(byteBuffer.copyOf(samplesRead * 2).toByteString())

                    // Update duration every ~1 second
                    durationTick += samplesRead
                    if (durationTick >= SAMPLE_RATE) {
                        durationSeconds++
                        durationTick = 0
                        // Update duration on live state if we have one
                        _liveCallState.value?.let {
                            _liveCallState.value = it.copy(durationSeconds = durationSeconds)
                        }
                    }
                }
            }

            audioRecord?.stop()
            audioRecord?.release()
            audioRecord = null
            Log.d(TAG, "🎙️ Microphone recording stopped")
        }
    }

    private fun handleServerMessage(text: String) {
        try {
            val json = JSONObject(text)
            when (json.optString("type")) {

                "caller_context" -> {
                    val caller = json.optJSONObject("caller")
                    val callerName = caller?.optString("name") ?: "Unknown"
                    val callerNumber = caller?.optString("phone_number") ?: "Unknown"
                    val isTrusted = caller?.optBoolean("trusted_contact") ?: false

                    _liveCallState.value = CallAnalysis(
                        callId = sessionId,
                        callerName = if (callerName == "null" || callerName.isEmpty()) "Unknown Caller" else callerName,
                        callerNumber = callerNumber,
                        durationSeconds = 0,
                        overallRiskScore = 0,
                        voiceRiskScore = 0,
                        scamRiskScore = 0,
                        identityRiskScore = 0,
                        detectedSignals = emptyList(),
                        riskHistory = emptyList(),
                        timestamp = "Live Now",
                        isLive = true
                    )
                    Log.d(TAG, "Caller context received. Trusted=$isTrusted")
                }

                "analysis_update" -> {
                    val risk = json.optJSONObject("overall_risk")
                    val score = risk?.optInt("score") ?: 0
                    val severity = risk?.optString("level") ?: "LOW"

                    val voice = json.optJSONObject("voice_authenticity")
                    val voiceRisk = ((voice?.optDouble("fake_probability") ?: 0.0) * 100).toInt()

                    val scam = json.optJSONObject("scam_behavior")
                    val scamScore = scam?.optInt("score") ?: 0

                    val identity = json.optJSONObject("identity")
                    val identityRisk = identity?.optInt("identity_risk") ?: 0
                    val claimedId = identity?.optString("claimed_identity") ?: "UNKNOWN"

                    val speech = json.optJSONObject("speech")
                    val transcript = speech?.optString("text") ?: ""

                    // Parse scam signals
                    val signals = scam?.optJSONArray("signals")
                    val newSignals = mutableListOf<RiskSignal>()
                    if (signals != null) {
                        for (i in 0 until signals.length()) {
                            val sig = signals.getJSONObject(i)
                            val sigType = sig.optString("type")
                            val sigConf = sig.optDouble("confidence")
                            val riskLvl = when {
                                sigConf > 0.8 -> RiskLevel.CRITICAL
                                sigConf > 0.5 -> RiskLevel.HIGH
                                else -> RiskLevel.MEDIUM
                            }
                            newSignals.add(RiskSignal(
                                title = sigType.replace("_", " ").lowercase().replaceFirstChar { it.uppercase() },
                                description = "Detected with ${(sigConf * 100).toInt()}% confidence",
                                severity = riskLvl
                            ))
                        }
                    }

                    if (voiceRisk > 70) {
                        newSignals.add(0, RiskSignal(
                            title = "Synthetic voice detected",
                            description = "AASIST fake probability: ${voiceRisk}%",
                            severity = RiskLevel.CRITICAL
                        ))
                    }

                    riskHistory.add(score)
                    detectedSignals.clear()
                    detectedSignals.addAll(newSignals)

                    _liveCallState.value = _liveCallState.value?.copy(
                        overallRiskScore = score,
                        voiceRiskScore = voiceRisk,
                        scamRiskScore = scamScore,
                        identityRiskScore = identityRisk,
                        claimedIdentity = if (claimedId == "UNKNOWN") null else claimedId,
                        detectedSignals = detectedSignals.toList(),
                        riskHistory = riskHistory.toList()
                    ) ?: CallAnalysis(
                        callId = sessionId,
                        callerName = "Live Call",
                        callerNumber = "Unknown",
                        durationSeconds = durationSeconds,
                        overallRiskScore = score,
                        voiceRiskScore = voiceRisk,
                        scamRiskScore = scamScore,
                        identityRiskScore = identityRisk,
                        claimedIdentity = if (claimedId == "UNKNOWN") null else claimedId,
                        detectedSignals = detectedSignals.toList(),
                        riskHistory = riskHistory.toList(),
                        timestamp = "Live Now",
                        isLive = true
                    )
                    Log.d(TAG, "📊 Risk update: score=$score level=$severity transcript=$transcript")
                }

                "risk_escalation" -> {
                    val newLevel = json.optString("new_level")
                    Log.w(TAG, "⚠️ Risk escalated to: $newLevel")
                }

                "risk_event" -> {
                    val event = json.optString("event")
                    val msg = json.optString("message")
                    Log.w(TAG, "🚨 Risk event: $event → $msg")
                }

                "pong" -> Log.d(TAG, "Pong received ✅")

                "error" -> {
                    val code = json.optString("code")
                    val msg = json.optString("message")
                    Log.e(TAG, "Server error: $code — $msg")
                }

                else -> Log.d(TAG, "Unknown message type: ${json.optString("type")}")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error parsing server message: ${e.message}")
        }
    }

    fun sendStop() {
        webSocket?.send(JSONObject().apply { put("type", "stop") }.toString())
    }

    fun disconnect() {
        isStreaming.set(false)
        micJob?.cancel()
        sendStop()
        webSocket?.close(1000, "User ended session")
        webSocket = null
        _connectionState.value = ConnectionState.DISCONNECTED

        // Move live call to "ended" state
        val ended = _liveCallState.value?.copy(isLive = false, timestamp = "Just Now")
        _liveCallState.value = null
    }

    private fun stopMicCapture() {
        isStreaming.set(false)
        micJob?.cancel()
    }

    private fun hasMicPermission(): Boolean =
        ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) ==
                PackageManager.PERMISSION_GRANTED

    enum class ConnectionState {
        DISCONNECTED, CONNECTING, CONNECTED, ERROR
    }
}
