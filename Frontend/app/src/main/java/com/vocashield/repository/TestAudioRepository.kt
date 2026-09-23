package com.vocashield.repository

import android.util.Log
import com.vocashield.models.CallAnalysis
import com.vocashield.models.RiskLevel
import com.vocashield.models.RiskSignal
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException

data class TestSample(
    val id: String,
    val filename: String,
    val category: String,
    val displayName: String,
    val durationSeconds: Double
)

class TestAudioRepository(private val backendUrl: String = "127.0.0.1:8000") {
    private val client = OkHttpClient()

    private fun getBaseUrl(): String {
        val host = if (backendUrl.contains("://")) backendUrl else "http://$backendUrl"
        return "$host/api/v1/test-audio"
    }

    suspend fun getTestSamples(): List<TestSample> = withContext(Dispatchers.IO) {
        val request = Request.Builder().url(getBaseUrl()).build()
        try {
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) return@withContext emptyList()
                val json = JSONObject(response.body?.string() ?: "")
                val samples = json.optJSONArray("samples") ?: return@withContext emptyList()
                val list = mutableListOf<TestSample>()
                for (i in 0 until samples.length()) {
                    val obj = samples.getJSONObject(i)
                    list.add(
                        TestSample(
                            id = obj.getString("id"),
                            filename = obj.getString("filename"),
                            category = obj.getString("category"),
                            displayName = obj.getString("display_name"),
                            durationSeconds = obj.getDouble("duration_seconds")
                        )
                    )
                }
                list
            }
        } catch (e: Exception) {
            Log.e("TestAudioRepo", "Failed to fetch samples: ${e.message}")
            emptyList()
        }
    }

    suspend fun analyzeSample(sampleId: String): CallAnalysis? = withContext(Dispatchers.IO) {
        val request = Request.Builder()
            .url("${getBaseUrl()}/$sampleId/analyze")
            .post("".toRequestBody())
            .build()

        try {
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) return@withContext null
                val json = JSONObject(response.body?.string() ?: "")
                
                // Parse the response into our CallAnalysis object
                val analysisId = json.optString("analysis_id", sampleId)
                val df = json.optJSONObject("deepfake")
                val voiceRisk = ((df?.optDouble("fake_probability", 0.0) ?: 0.0) * 100).toInt()
                
                val scam = json.optJSONObject("scam_analysis")
                val scamScore = scam?.optInt("scam_behavior_score", 0) ?: 0
                val signals = scam?.optJSONArray("signals")
                val signalList = mutableListOf<RiskSignal>()
                if (signals != null) {
                    for (i in 0 until signals.length()) {
                        val sig = signals.getJSONObject(i)
                        val conf = sig.optDouble("confidence", 0.0)
                        val lvl = if (conf > 0.8) RiskLevel.CRITICAL else if (conf > 0.5) RiskLevel.HIGH else RiskLevel.MEDIUM
                        signalList.add(RiskSignal(title = sig.optString("type"), description = "Confidence: ${(conf*100).toInt()}%", severity = lvl))
                    }
                }
                
                val risk = json.optJSONObject("risk_assessment")
                val totalScore = risk?.optInt("overall_risk_score", 0) ?: 0
                
                val id = risk?.optJSONObject("identity")
                val idRisk = id?.optInt("identity_risk", 0) ?: 0
                
                val transcript = json.optString("transcription", "")
                
                val ts = json.optJSONObject("test_sample")
                val callerName = ts?.optString("id", sampleId) ?: sampleId
                val groundTruth = ts?.optString("ground_truth", "") ?: ""
                
                CallAnalysis(
                    callId = analysisId,
                    callerName = "Test Sample: $callerName",
                    callerNumber = "GT: $groundTruth",
                    durationSeconds = 0,
                    overallRiskScore = totalScore,
                    voiceRiskScore = voiceRisk,
                    scamRiskScore = scamScore,
                    identityRiskScore = idRisk,
                    detectedSignals = signalList,
                    riskHistory = emptyList(),
                    timestamp = "Just Now",
                    isLive = false
                )
            }
        } catch (e: Exception) {
            Log.e("TestAudioRepo", "Failed to analyze sample: ${e.message}")
            null
        }
    }
}

