import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_android_start_metadata():
    client = TestClient(app)
    with client.websocket_connect("/ws/call/WS_ANDR_001") as websocket:
        # 1. START metadata
        websocket.send_json({
            "type": "START",
            "caller": {
                "phone_number": "+919876543210",
                "call_direction": "INCOMING"
            }
        })
        
        ctx_reply = websocket.receive_json()
        assert ctx_reply["type"] == "caller_context"
        assert ctx_reply["caller"]["phone_number"] == "+919876543210"

def test_android_malformed_json():
    client = TestClient(app)
    with client.websocket_connect("/ws/call/WS_ANDR_002") as websocket:
        # Invalid payload formats handled gracefully
        websocket.send_text("INVALID JSON")
        # should not crash
        
def test_android_verification_passthrough():
    client = TestClient(app)
    with client.websocket_connect("/ws/call/WS_ANDR_003") as websocket:
        websocket.send_json({
            "type": "START",
            "caller": {"phone_number": "+919876543210"}
        })
        websocket.receive_json() # flush ctx
        
        websocket.send_json({
            "type": "VERIFICATION",
            "status": "PASSED"
        })
        websocket.send_json({"type": "STOP"})
        
        # flush risk events which might be timeline logs
        while True:
            resp = websocket.receive_json()
            if resp["type"] == "session_summary":
                break

def test_android_ping_pong():
    client = TestClient(app)
    with client.websocket_connect("/ws/call/WS_ANDR_004") as websocket:
        websocket.send_json({"type": "PING"})
        resp = websocket.receive_json()
        assert resp["type"] == "pong"
