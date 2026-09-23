import pytest
from app.engines.risk_engine import risk_engine
from app.engines.identity_engine import identity_engine
from app.engines.attack_pattern_engine import attack_pattern_engine
from app.engines.verification_engine import verification_engine
from app.engines.scam_signal_engine import signal_engine

def run_pipeline(transcript, context, fake_prob=0.0):
    scam_res = signal_engine.analyze(transcript)
    id_res = identity_engine.extract_claimed_identity(transcript)
    
    # Merge context with derived
    context["claimed_identity"] = id_res["claimed_identity"]
    
    risk_metrics = risk_engine.calculate_risk({"fake_probability": fake_prob}, scam_res, context)
    patterns = attack_pattern_engine.classify(risk_metrics, scam_res, context)
    return risk_metrics, patterns

def test_known_trusted_contact():
    ctx = {"number_known": True, "trusted_contact": True, "verification_status": "NOT_AVAILABLE"}
    risk, patterns = run_pipeline("Hey I'm your brother, let's get dinner.", ctx)
    assert risk["identity"]["identity_risk"] <= 20
    assert risk["identity"]["identity_match"] == True

def test_unknown_number_family_impersonation():
    ctx = {"number_known": False, "trusted_contact": False, "verification_status": "NOT_AVAILABLE"}
    risk, patterns = run_pipeline("I'm your brother. Send me money.", ctx)
    assert risk["identity"]["identity_risk"] >= 70
    assert risk["identity"]["identity_match"] == False

def test_bank_impersonation():
    ctx = {"number_known": False, "trusted_contact": False}
    risk, patterns = run_pipeline("This is your bank. Give me the OTP.", ctx)
    assert "AUTHORITY_IMPERSONATION" in patterns

def test_police_impersonation():
    ctx = {"number_known": False, "trusted_contact": False}
    risk, patterns = run_pipeline("I am from the police. You are under arrest unless you pay.", ctx)
    assert "AUTHORITY_IMPERSONATION" in patterns
    
def test_identity_mismatch():
    # Known trusted number, but claims to be "Bank" instead of "brother" -- conceptually in our system,
    # right now, we haven't strictly tied contact class to identity categories yet except mismatch triggers.
    pass

def test_verification_passed():
    ctx = {"number_known": False, "trusted_contact": False, "verification_status": "PASSED"}
    risk, patterns = run_pipeline("I'm your brother.", ctx)
    # Passed verification heavily lowers identity risk
    assert risk["identity"]["identity_risk"] < 70

def test_verification_failed():
    ctx = {"number_known": False, "trusted_contact": False, "verification_status": "FAILED"}
    risk, patterns = run_pipeline("I'm your brother.", ctx)
    assert risk["identity"]["identity_risk"] == 100
    assert risk["identity"]["identity_match"] == False

def test_missing_caller_metadata():
    ctx = {}
    risk, patterns = run_pipeline("hello.", ctx)
    assert risk["identity"]["known_number"] == False
