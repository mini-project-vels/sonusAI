# Android Integration Contract

VocaShield AI is designed to integrate into Android applications via a local WebSocket stream acting on a highly-controlled audio flow.

## Critical Platform Constraint
Android specifically guards cellular voice hardware streams. Do not attempt to bypass `CallScreeningService` constraints. Rather, route telephony metadata via `CallScreeningService` and capture audio via:
- In-App WebRTC/VoIP.
- Intentional, consented microphone loops (e.g. putting a scam call on speakerphone).
- Specifically approved accessibility integrations.

## WebSocket Protocol
Connect locally or remotely via: `ws://<backend_url>/ws/call/{session_id}`

### 1. Session Initialization (START)
Once connected, Android must initialize call context:
```json
{
  "type": "START",
  "caller": {
    "phone_number": "+919876543210",
    "call_direction": "INCOMING"
  },
  "device": {
    "platform": "android",
    "app_version": "1.0"
  }
}
```

### 2. Audio Streaming (Continuous)
Send raw binary chunks (16-bit signed PCM, mono, 16kHz, little-endian).
Preferred chunk sizes: 20-100KB (1-3 seconds of audio). No WAV headers.

### 3. Server Responses
The server will asynchronously push analytics updates:
- **`caller_context`**: Matches initial database validations against `START`.
- **`analysis_update`**: Real-time overlapping risk models encapsulating voice authenticity, speech-to-text, scam risk, and overall trajectory. Includes `audio_quality` stats.
- **`risk_event`**: Discrete events like `FINANCIAL_REQUEST` or `IMPERSONATION_DETECTED` mapping to your visual timeline.
- **`risk_escalation`**: Emitted linearly as risk shifts boundaries (e.g., `MEDIUM` -> `HIGH`).

### 4. Explicit Authentication / Verification
If an impersonation event flags `HIGH`, the user can query their specific contact challenge. Post resolution, the Android client should transmit:
```json
{
  "type": "VERIFICATION",
  "status": "PASSED"
}
```
Options: `PASSED`, `FAILED`, `SKIPPED`, `NOT_AVAILABLE`.

### 5. Keeping Connections Alive & Tear-down
Send `{"type": "PING"}` to sustain long loads. 
End session cleanly by sending `{"type": "STOP"}` and await the `session_summary` confirmation.
