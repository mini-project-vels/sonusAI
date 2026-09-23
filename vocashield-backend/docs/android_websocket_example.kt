/**
 * VocaShield AI - Controlled Audio Capture WebSocket Example
 * 
 * IMPORTANT: This code is intended for processing in-app WebRTC or consented
 * internal microphone paths. It does NOT bypass Android cellular restrictions.
 */

import okhttp3.*
import okio.ByteString
import org.json.JSONObject
import java.nio.ByteBuffer
import java.util.concurrent.TimeUnit
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import kotlinx.coroutines.*

class VocashieldAndroidClient(private val sessionId: String, private val phoneNumber: String) {
    
    private val client = OkHttpClient.Builder()
        .readTimeout(0, TimeUnit.MILLISECONDS)
        .build()
        
    private var webSocket: WebSocket? = null
    private var isRecording = false
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    fun connectAndStart(serverUrl: String) {
        val request = Request.Builder()
            .url("$serverUrl/ws/call/$sessionId")
            .build()
            
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                // 1. Send START Metadata
                val startMsg = JSONObject().apply {
                    put("type", "START")
                    put("caller", JSONObject().apply {
                        put("phone_number", phoneNumber)
                        put("call_direction", "INCOMING")
                    })
                }
                webSocket.send(startMsg.toString())
                
                // 2. Start capturing audio (Consent Required!)
                startAudioCapture()
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                // Handle analytics / timeline / events
                val json = JSONObject(text)
                when (json.optString("type")) {
                    "analysis_update" -> {
                        val risk = json.getJSONObject("risk_assessment").getString("risk_level")
                        println("Live Risk Level: $risk")
                    }
                    "risk_event" -> println("Event Detected: ${json.getString("event")}")
                    "risk_escalation" -> println("Escalation: ${json.getString("new_level")}")
                    "session_summary" -> {
                        println("End of Call Summary: $text")
                        close()
                    }
                }
            }
            
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                t.printStackTrace()
                isRecording = false
            }
        })
    }

    private fun startAudioCapture() {
        isRecording = true
        scope.launch {
            val sampleRate = 16000
            val minBufferSize = AudioRecord.getMinBufferSize(
                sampleRate,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT
            )
            
            val audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                sampleRate,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                minBufferSize * 10
            )

            val buffer = ByteArray(32000) // approx 1 sec
            audioRecord.startRecording()

            try {
                while (isRecording) {
                    val read = audioRecord.read(buffer, 0, buffer.size)
                    if (read > 0) {
                        webSocket?.send(ByteString.of(buffer, 0, read))
                    }
                }
            } finally {
                audioRecord.stop()
                audioRecord.release()
            }
        }
    }

    fun submitVerification(passed: Boolean) {
        val payload = JSONObject().apply {
            put("type", "VERIFICATION")
            put("status", if (passed) "PASSED" else "FAILED")
        }
        webSocket?.send(payload.toString())
    }

    fun stopSession() {
        isRecording = false
        val stopMsg = JSONObject().apply { put("type", "STOP") }
        webSocket?.send(stopMsg.toString())
    }

    fun close() {
        isRecording = false
        webSocket?.close(1000, "User Request")
        scope.cancel()
    }
}
