import pytest
from app.services.call_session import CallSession, session_manager

def test_session_lifecycle():
    session = session_manager.create_session("TEST_LIFECYCLE")
    assert session.session_id == "TEST_LIFECYCLE"
    assert session_manager.active_sessions_count == 1
    
    sess2 = session_manager.get_session("TEST_LIFECYCLE")
    assert sess2 == session
    
    session_manager.close_session("TEST_LIFECYCLE")
    assert session_manager.active_sessions_count == 0

def test_transcript_aggregation():
    session = CallSession("TR")
    session.add_transcript("Hello.")
    session.add_transcript("How are you?")
    assert session.get_full_transcript() == "Hello. How are you?"
