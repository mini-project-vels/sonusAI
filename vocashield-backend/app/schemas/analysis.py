from pydantic import BaseModel
from typing import Optional

class AudioMetadata(BaseModel):
    duration_seconds: float
    original_sample_rate: int
    processed_sample_rate: int
    original_channels: int
    processed_channels: int

class DeepfakePrediction(BaseModel):
    fake_probability: float
    real_probability: float
    prediction: str
    model: str
    metadata: dict

class TranscriptionResponse(BaseModel):
    text: str
    language: str

class SignalDetail(BaseModel):
    detected: bool
    confidence: float
    evidence: list[str]

class ScamAnalysisResponse(BaseModel):
    scam_behavior_score: int
    signals: dict[str, SignalDetail]
    
class ContextInfo(BaseModel):
    number_known: bool = False
    trusted_contact: bool = False
    claimed_identity: str | None = None
    verification_status: str = "NOT_AVAILABLE"
    
class ContextIdentity(BaseModel):
    known_number: bool
    trusted_contact: bool
    claimed_identity: str
    identity_match: bool
    identity_risk: int
    verification_status: str

class RiskFactor(BaseModel):
    factor: str
    score: int
    contribution: str

class RiskAssessmentResponse(BaseModel):
    voice_risk: int
    scam_behavior_risk: int
    context_risk: int
    
    identity: ContextIdentity
    
    overall_risk_score: int
    risk_level: str
    
    risk_factors: list[RiskFactor]
    attack_patterns: list[str]
    recommendations: list[str]
    
class AnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    processing_time_ms: int
    audio: AudioMetadata
    deepfake: DeepfakePrediction
    transcription: TranscriptionResponse
    scam_analysis: ScamAnalysisResponse
    risk_assessment: RiskAssessmentResponse
