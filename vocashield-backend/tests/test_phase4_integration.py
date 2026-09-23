import pytest
from app.engines.risk_engine import risk_engine
from app.engines.attack_pattern_engine import attack_pattern_engine
from app.engines.verification_engine import verification_engine
from app.engines.scam_signal_engine import signal_engine

def get_integrated_pipeline(fake_prob, transcript, context):
    scam_results = signal_engine.analyze(transcript)
    deepfake = {"fake_probability": fake_prob, "real_probability": 1.0 - fake_prob}
    
    risk_metrics = risk_engine.calculate_risk(deepfake, scam_results, context)
    patterns = attack_pattern_engine.classify(risk_metrics, scam_results, context)
    recs = verification_engine.generate_recommendations(risk_metrics, patterns, scam_results)
    
    return risk_metrics, patterns, recs

def test_genuine_normal_conversation():
    # Real voice, normal conversation, known trusted contact
    transcript = "Hello, I wanted to ask if you are free this evening. Let's have dinner."
    context = {"number_known": True, "trusted_contact": True}
    
    risk_metrics, patterns, recs = get_integrated_pipeline(0.01, transcript, context)
    
    assert risk_metrics["risk_level"] in ["LOW", "MEDIUM"]
    assert risk_metrics["overall_risk_score"] < 50
    assert risk_metrics["voice_risk"] < 10

def test_ai_voice_harmless_conversation():
    # High AASIST, normal conversation, known contact
    transcript = "Hey, just planning out the schedule for tomorrow. See you then."
    context = {"number_known": True, "trusted_contact": True}
    
    risk_metrics, patterns, recs = get_integrated_pipeline(0.95, transcript, context)
    
    # Voice risk high
    assert risk_metrics["voice_risk"] == 95
    # Overall risk shouldn't be zero because it's an AI voice, but we shouldn't necessarily flag it as a highly critical behavioral scam
    
    # Verify explanation highlights synthetic voice but distinct from scam behavior
    factors = [f["factor"] for f in risk_metrics["risk_factors"]]
    assert "Synthetic voice characteristics" in factors
    assert risk_metrics["scam_behavior_risk"] == 0

def test_human_scammer():
    # Low fake probability, high scam behavior, unknown number
    transcript = "This is your bank customer support. Tell me the OTP you just received or your account will be blocked."
    context = {"number_known": False, "trusted_contact": False, "claimed_identity": "support"}
    
    risk_metrics, patterns, recs = get_integrated_pipeline(0.05, transcript, context)
    
    assert risk_metrics["voice_risk"] < 10
    assert risk_metrics["scam_behavior_risk"] > 50
    assert "OTP_CREDENTIAL_SCAM" in patterns
    assert "AUTHORITY_IMPERSONATION" in patterns

def test_ai_voice_financial_scam():
    # High fake prob, financial request, urgency, impersonation, unknown number
    transcript = "Hi son, I am in an emergency. Please transfer 50000 rupees immediately. Send it to this upi immediately. Don't tell anyone."
    context = {"number_known": False, "trusted_contact": False, "claimed_identity": "son"}
    
    risk_metrics, patterns, recs = get_integrated_pipeline(0.99, transcript, context)
    
    assert risk_metrics["risk_level"] == "CRITICAL"
    assert "AI_VOICE_IMPERSONATION" in patterns
    assert "FINANCIAL_SCAM" in patterns
    assert "FAMILY_IMPERSONATION" in patterns
