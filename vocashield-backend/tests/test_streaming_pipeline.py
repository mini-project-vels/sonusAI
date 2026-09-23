import pytest
import time
from fastapi.testclient import TestClient
from app.main import app

def test_websocket_streaming_pipeline():
    client = TestClient(app)
    with client.websocket_connect("/ws/call/WS_STREAM_001") as websocket:
        websocket.send_json({"type": "start"})
        
        ctx_reply = websocket.receive_json()
        assert ctx_reply["type"] == "caller_context"
        
        chunk = bytearray(32000)
        websocket.send_bytes(bytes(chunk))
        
        websocket.send_json({"type": "stop"})
        summary = websocket.receive_json()
        assert summary["type"] == "session_summary"
