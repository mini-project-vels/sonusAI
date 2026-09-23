import pytest
from app.engines.risk_engine import risk_engine

def test_risk_level_low_boundaries():
    res = risk_engine.calculate_risk(
        {"fake_probability": 0.05}, 
        {"scam_behavior_score": 0, "signals": {}}, 
        {"number_known": True, "trusted_contact": True}
    )
    assert res["risk_level"] == "LOW"
    assert res["overall_risk_score"] < 25

def test_risk_level_critical():
    res = risk_engine.calculate_risk(
        {"fake_probability": 0.99}, 
        {"scam_behavior_score": 95, "signals": {}}, 
        {"number_known": False, "trusted_contact": False}
    )
    assert res["risk_level"] == "CRITICAL"
    assert res["overall_risk_score"] >= 75

def test_missing_context():
    res = risk_engine.calculate_risk({"fake_probability": 0.5}, {"scam_behavior_score": 50}, None)
    # Shouldn't crash
    assert "overall_risk_score" in res
