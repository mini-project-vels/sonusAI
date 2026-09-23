package com.vocashield.network

import com.vocashield.models.DeepfakeResult

/**
 * Interface ready for Phase 1 FastAPI `/api/v1/analyze` backend integration.
 */
interface ApiService {
    suspend fun analyzeAudioChunk(audioBytes: ByteArray): DeepfakeResult
}

class MockApiService : ApiService {
    override suspend fun analyzeAudioChunk(audioBytes: ByteArray): DeepfakeResult {
        return DeepfakeResult(
            fakeProbability = 0.87f,
            realProbability = 0.13f,
            prediction = "FAKE"
        )
    }
}
