import pytest
from app.engines.verification_engine import verification_engine

def test_recommendation_generation():
    risk_assessment = {"voice_risk": 99, "risk_level": "CRITICAL"}
    attack_patterns = ["AI_VOICE_IMPERSONATION"]
    scam_signals = {
        "signals": {
            "impersonation": {"detected": True},
            "financial_request": {"detected": True}
        }
    }
    
    recs = verification_engine.generate_recommendations(risk_assessment, attack_patterns, scam_signals)
    
    # Needs to uniquely track the specific rules
    assert "Voice characteristics indicate possible synthetic or manipulated audio." in recs
    assert "Do not transfer money during the call." in recs
    assert "Do not act on instructions from this caller until their identity is independently verified." in recs
