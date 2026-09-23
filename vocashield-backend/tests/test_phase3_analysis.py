import pytest
from app.engines.scam_signal_engine import signal_engine

def test_phase3_test1():
    transcript = "Hi son, I am in an emergency. Please transfer 50000 rupees immediately. Don't tell anyone."
    res = signal_engine.analyze(transcript)["signals"]
    assert res["financial_request"]["detected"] is True
    assert res["urgency"]["detected"] is True
    assert res["secrecy"]["detected"] is True
    assert res["impersonation"]["detected"] is True
    
def test_phase3_test2():
    transcript = "Hello, I wanted to ask if you are free this evening. Let's have dinner."
    score = signal_engine.analyze(transcript)["scam_behavior_score"]
    assert score == 0

def test_phase3_test3():
    transcript = "This is your bank customer support. Tell me the OTP you just received or your account will be blocked."
    res = signal_engine.analyze(transcript)["signals"]
    assert res["credential_request"]["detected"] is True
    assert res["impersonation"]["detected"] is True
    assert res["threat_or_pressure"]["detected"] is True
    
def test_phase3_test4():
    transcript = "Please scan this QR code and send the payment to this UPI ID immediately."
    res = signal_engine.analyze(transcript)["signals"]
    assert res["payment_redirection"]["detected"] is True
    assert res["financial_request"]["detected"] is True
    assert res["urgency"]["detected"] is True
