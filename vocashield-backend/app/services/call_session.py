import time
import numpy as np

class CallSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = time.time()
        self.audio_buffer = bytearray()
        self.chunks_received = 0
        self.total_audio_seconds = 0.0
        self.last_analysis_time = 0.0
        
        self.current_risk = 0
        self.current_risk_level = "LOW"
        
        # Phase 6 Additions
        self.caller_phone_number = None
        self.call_direction = "UNKNOWN"
        self.verification_status = "NOT_AVAILABLE"
        
        self.risk_history = []
        self.transcript_history = []
        self.detected_signals = set()
        self.attack_patterns = []
        self.event_timeline = []

    def get_masked_phone(self) -> str:
        if not self.caller_phone_number:
            return "UNKNOWN"
        ph = self.caller_phone_number
        if len(ph) <= 7:
            return ph
        return ph[:3] + "*" * (len(ph) - 7) + ph[-4:]

    def add_event(self, event_type: str, description: str):
        self.event_timeline.append({
            "type": "risk_event",
            "timestamp": int(time.time() - self.start_time),
            "event": event_type,
            "description": description
        })
        
    def get_full_transcript(self, joiner=" ") -> str:
        return joiner.join(self.transcript_history)
        
    def add_transcript(self, text: str):
        if text:
             self.transcript_history.append(text)
             
    def add_risk_point(self, risk_score: int, timestamp: int):
        self.risk_history.append({
             "timestamp": timestamp,
             "risk_score": risk_score
        })

class CallSessionManager:
    def __init__(self):
        self._sessions = {}

    def create_session(self, session_id: str) -> CallSession:
        session = CallSession(session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> CallSession:
        return self._sessions.get(session_id)

    def update_session(self, session: CallSession):
        self._sessions[session.session_id] = session

    def close_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]

    @property
    def active_sessions_count(self) -> int:
        return len(self._sessions)

session_manager = CallSessionManager()
