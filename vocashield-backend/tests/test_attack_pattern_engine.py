import pytest
from app.engines.attack_pattern_engine import attack_pattern_engine

def test_attack_impersonation():
    risk_assessment = {"voice_risk": 90, "overall_risk_score": 85}
    scam_signals = {
        "signals": {
            "impersonation": {"detected": True, "evidence": ["son"]}
        }
    }
    
    patterns = attack_pattern_engine.classify(risk_assessment, scam_signals, None)
    
    assert "AI_VOICE_IMPERSONATION" in patterns
    assert "FAMILY_IMPERSONATION" in patterns

def test_financial_scam():
    risk_assessment = {}
    scam_signals = {
        "signals": {
            "financial_request": {"detected": True}
        }
    }
    patterns = attack_pattern_engine.classify(risk_assessment, scam_signals, None)
    assert "FINANCIAL_SCAM" in patterns
