import pytest
from app.engines.identity_engine import identity_engine

def test_extract_brother():
    res = identity_engine.extract_claimed_identity("I am your brother. Send me money.")
    assert res["claimed_identity"] == "FAMILY_MEMBER"
    
def test_extract_bank():
    res = identity_engine.extract_claimed_identity("This is your bank calling.")
    assert res["claimed_identity"] == "BANK"
    
def test_extract_unknown():
    res = identity_engine.extract_claimed_identity("hey man how are you doing")
    assert res["claimed_identity"] == "UNKNOWN"
