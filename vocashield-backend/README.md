# VocaShield AI Backend

## Phase 5 Real-Time WebSocket API

The backend currently enables live real-time deepfake & scam tracking natively via WebSockets.

### WebSocket endpoint: `/ws/call/{session_id}`

The Android application connects here and pushes chunks iteratively representing rolling live execution.

1. **Connection**: Connect via `ws://<host>:<port>/ws/call/{session_id}`.
2. **Audio format**: Must be uncompressed PCM, 16-bit, mono channel, locked strictly at `16000 Hz`.
3. **START message**: `{ "type": "start" }`. Send immediately after connection.
4. **Binary audio chunks**: Push raw binary `bytes` (e.g. 1–2 seconds frames). The backend natively merges and rolls buffer windows.
5. **Analysis update**: Server triggers: `{ "type": "analysis_update", "deepfake": {...}, "risk_assessment": {...} }`.
6. **Risk events**: Dynamically alerts: `{ "type": "risk_event", "event": "FINANCIAL_REQUEST_DETECTED" }` or `risk_escalation`.
7. **STOP message**: End session elegantly by sending text payload: `{ "type": "stop" }`.
8. **Session summary**: Returns global analytics payload `{ "type": "session_summary", "final_risk_score": 90 }`.

### Test Streaming Client
You can natively replay any valid 16kHz `.wav` to test via the testing script natively built:
```bash
python scripts/test_websocket.py test_audio/scam.wav
```
This script acts strictly as an Android proxy triggering start, shipping bytes synchronously simulating latency, awaiting AI background streams, and printing final evaluation summaries.
