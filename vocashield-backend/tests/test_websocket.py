import pytest
import numpy as np
from fastapi.testclient import TestClient
from app.main import app

def test_websocket_start_stop():
    client = TestClient(app)
    with client.websocket_connect("/ws/call/WS_TEST_001") as websocket:
        websocket.send_json({"type": "start"})
        
        ctx_reply = websocket.receive_json()
        assert ctx_reply["type"] == "caller_context"
        
        # send broken bytes string
        websocket.send_bytes(b"\x00\x01\x02")
        error_resp = websocket.receive_json()
        assert error_resp["type"] == "error"
        assert error_resp["code"] == "INVALID_AUDIO_FORMAT"
        
        websocket.send_json({"type": "stop"})
        summary = websocket.receive_json()
        
        assert summary["type"] == "session_summary"
        assert summary["session_id"] == "WS_TEST_001"
        assert "final_risk_score" in summary
