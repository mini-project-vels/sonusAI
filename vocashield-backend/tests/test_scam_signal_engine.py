import pytest
from app.engines.scam_signal_engine import signal_engine

def test_engine_financial_and_urgency():
    transcript = "Hi son, I am in an emergency. Please transfer 50000 rupees immediately. Don't tell anyone."
    res = signal_engine.analyze(transcript)
    
    sigs = res["signals"]
    assert sigs["financial_request"]["detected"] is True
    assert sigs["urgency"]["detected"] is True
    assert sigs["secrecy"]["detected"] is True
    assert sigs["impersonation"]["detected"] is True
    
    assert res["scam_behavior_score"] > 50

def test_engine_normal_conversation():
    transcript = "Hello, I wanted to ask if you are free this evening. Let's have dinner."
    res = signal_engine.analyze(transcript)
    
    for category, details in res["signals"].items():
        assert details["detected"] is False
    
    assert res["scam_behavior_score"] == 0

def test_engine_credential_threat():
    transcript = "This is your bank customer support. Tell me the OTP you just received or your account will be blocked."
    res = signal_engine.analyze(transcript)
    
    sigs = res["signals"]
    assert sigs["credential_request"]["detected"] is True
    assert sigs["impersonation"]["detected"] is True
    assert sigs["threat_or_pressure"]["detected"] is True

def test_engine_payment_redirection():
    transcript = "Please scan this QR code and send the payment to this UPI ID immediately."
    res = signal_engine.analyze(transcript)
    
    sigs = res["signals"]
    assert sigs["payment_redirection"]["detected"] is True
    assert sigs["financial_request"]["detected"] is True
    assert sigs["urgency"]["detected"] is True
