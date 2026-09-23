package com.vocashield.models

/**
 * Data response matching the AASIST / Deepfake FastAPI backend output.
 */
data class DeepfakeResult(
    val fakeProbability: Float,
    val realProbability: Float,
    val prediction: String // "FAKE" or "REAL"
)
