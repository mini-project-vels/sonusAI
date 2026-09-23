import asyncio
import json
import logging
import time
import numpy as np
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.config import settings
from app.services.call_session import session_manager, CallSession
from app.models.deepfake_detector import detector
from app.models.speech_to_text import transcriber
from app.engines.scam_signal_engine import signal_engine
from app.engines.risk_engine import risk_engine
from app.engines.attack_pattern_engine import attack_pattern_engine
from app.engines.verification_engine import verification_engine
from app.engines.identity_engine import identity_engine

router = APIRouter()
logger = logging.getLogger(__name__)

analysis_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_ANALYSES)

def run_synchronous_pipeline(session_id: str, audio_float: np.ndarray, current_transcript: str):
    t_start = time.time()
    
    # 1. AASIST (Deepfake) logic
    t0 = time.time()
    try:
        deepfake_result = detector.predict(audio_float, 16000)
    except Exception as e:
        deepfake_result = {"fake_probability": 0.0, "real_probability": 0.0, "prediction": "UNKNOWN"}
    aasist_ms = int((time.time() - t0) * 1000)
    
    # 2. Whisper Transcription 
    # To keep context building without rescanning 1h of audio, we could just feed this chunk and append.
    # However, if we're only passing chunk, Whisper might miss words split at boundary. 
    # MVP logic: transcribe chunk, append. (In real-world we'd use a small rolling overlap or faster-whisper stream).
    t0 = time.time()
    try:
        whisper_result = transcriber.transcribe(audio_float, 16000)
        chunk_text = whisper_result.get("text", "")
    except Exception:
        whisper_result = {"text": "", "language": "en"}
        chunk_text = ""
    whisper_ms = int((time.time() - t0) * 1000)
    
    # 3. Scam Signals
    t0 = time.time()
    full_text = current_transcript
    if chunk_text:
        full_text = (full_text + " " + chunk_text).strip()
    
    scam_result = signal_engine.analyze(full_text)
    scam_ms = int((time.time() - t0) * 1000)
    
    # NEW 4. Identity Engine matching
    t0 = time.time()
    identity_result = identity_engine.extract_claimed_identity(full_text)
    identity_ms = int((time.time() - t0) * 1000)
    
    # 5. Risk Engine
    t0 = time.time()
    from app.services.call_session import session_manager
    session_obj = session_manager.get_session(session_id)
    caller_phone = session_obj.caller_phone_number if session_obj else None
    
    from app.services.contact_service import contact_service
    matching_contact = contact_service.find_by_phone_number(caller_phone) if caller_phone else None
    
    context = {
        "number_known": matching_contact is not None,
        "trusted_contact": matching_contact.trusted if matching_contact else False,
        "claimed_identity": identity_result["claimed_identity"],
        "verification_status": session_obj.verification_status if session_obj else "NOT_AVAILABLE"
    } 
    risk_assessment = risk_engine.calculate_risk(deepfake_result, scam_result, context)
    risk_ms = int((time.time() - t0) * 1000)
    
    # 6. Audio Quality checks
    rms = max(float(np.sqrt(np.mean(audio_float**2))), 0.0)
    clipping_ratio = float(np.mean(np.abs(audio_float) >= 0.99))
    silence_ratio = float(np.mean(np.abs(audio_float) < 0.001))
    
    # Check if reliable
    analysis_confidence = "HIGH"
    if rms < 0.005 or clipping_ratio > 0.1:
         analysis_confidence = "LOW"
         
    hw_dur = len(audio_float) / 16000.0
         
    audio_quality = {
        "duration_seconds": round(hw_dur, 2),
        "rms": round(rms, 4),
        "clipping_ratio": round(clipping_ratio, 4),
        "silence_ratio": round(silence_ratio, 4),
        "analysis_confidence": analysis_confidence
    }

    attack_patterns = attack_pattern_engine.classify(risk_assessment, scam_result, context)
    recommendations = verification_engine.generate_recommendations(risk_assessment, attack_patterns, scam_result)
    
    risk_assessment["attack_patterns"] = attack_patterns
    risk_assessment["recommendations"] = recommendations
    
    total_ms = int((time.time() - t_start) * 1000)
    
    performance = {
        "preprocessing_ms": 0,
        "aasist_ms": aasist_ms,
        "whisper_ms": whisper_ms,
        "scam_analysis_ms": scam_ms,
        "risk_engine_ms": risk_ms,
        "total_analysis_ms": total_ms
    }
    
    # Create the phase 7 structured response natively
    return {
        "voice_authenticity": {
            "fake_probability": deepfake_result["fake_probability"],
            "label": "LIKELY_AI_GENERATED" if deepfake_result["prediction"] == "FAKE" else "HUMAN"
        },
        "speech": whisper_result,
        "scam_behavior": {
            "score": scam_result["scam_behavior_score"],
            "signals": [{"type": key.upper(), "confidence": val["confidence"]} for key, val in scam_result["signals"].items() if val["detected"]]
        },
        "identity": {
            "claimed_identity": context["claimed_identity"],
            "identity_risk": risk_assessment["identity"]["identity_risk"]
        },
        "overall_risk": {
            "score": risk_assessment["overall_risk_score"],
            "level": risk_assessment["risk_level"]
        },
        "attack_patterns": attack_patterns,
        "performance": performance,
        "chunk_text": chunk_text,
        "audio_quality": audio_quality
    }

async def analyze_background(websocket: WebSocket, session: CallSession, analysis_bytes: bytes):
    async with analysis_semaphore:
        try:
            # Preprocessing 16kHz mono int16 PCM -> float32
            audio = np.frombuffer(analysis_bytes, dtype=np.int16)
            audio_float = audio.astype(np.float32) / 32768.0
            
            # Send to blocking thread to unblock websockets loop
            current_transcript = session.get_full_transcript()
            result = await asyncio.to_thread(run_synchronous_pipeline, session.session_id, audio_float, current_transcript)
            
            session.add_transcript(result["chunk_text"])
            
            new_risk_score = result["overall_risk"]["score"]
            new_risk_level = result["overall_risk"]["level"]
            elapsed_seconds = int(time.time() - session.start_time)
            
            session.add_risk_point(new_risk_score, elapsed_seconds)
            
            # Event detection logic
            events_emitted = []
            
            # Check risk escalation
            if new_risk_level != session.current_risk_level:
                session.add_event("RISK_ESCALATION", f"Risk shifted to {new_risk_level}")
                escalation_msg = {
                    "type": "risk_escalation",
                    "previous_level": session.current_risk_level,
                    "new_level": new_risk_level,
                    "score": new_risk_score,
                    "reason": [s["type"] for s in result["scam_behavior"]["signals"]]
                }
                session.current_risk_level = new_risk_level
                events_emitted.append(escalation_msg)
                
            session.current_risk = new_risk_score
            
            # Check newly detected scam signals to trigger events
            detected_now = {s["type"] for s in result["scam_behavior"]["signals"]}
            new_signals = detected_now - session.detected_signals
            for sig in new_signals:
                event_name = f"{sig.upper()}_DETECTED"
                events_emitted.append({
                    "type": "risk_event",
                    "session_id": session.session_id,
                    "timestamp": elapsed_seconds,
                    "event": event_name,
                    "severity": "HIGH",
                    "message": f"A {sig.replace('_', ' ')} logic was detected."
                })
            session.detected_signals.update(new_signals)
            
            claimed = result["identity"]["claimed_identity"]
            if claimed != "UNKNOWN" and claimed not in session.detected_signals:
                session.detected_signals.add(claimed)
                session.add_event("IDENTITY_CLAIM", f"Caller claims to be a {claimed.replace('_', ' ').lower()}")
                events_emitted.append({
                    "type": "risk_event",
                    "timestamp": elapsed_seconds,
                    "event": "IDENTITY_CLAIM",
                    "description": f"Caller claims to be a {claimed.replace('_', ' ').lower()}"
                })
                
            has_imper = "FAMILY_IMPERSONATION" in result["attack_patterns"] or "AUTHORITY_IMPERSONATION" in result["attack_patterns"]
            if new_risk_level in ["HIGH", "CRITICAL"] and has_imper and "VERIFICATION_PROMPTED" not in session.detected_signals:
                 events_emitted.append({
                     "type": "verification_required",
                     "reason": "Caller claims to be a trusted contact but identity could not be independently verified.",
                     "recommended_action": "Ask the caller your private verification question."
                 })
                 session.detected_signals.add("VERIFICATION_PROMPTED")
            
            # Track attack patterns for summary
            session.attack_patterns = result["attack_patterns"]
            
            update_msg = {
                "type": "analysis_update",
                "session_id": session.session_id,
                "timestamp": int(time.time()),
                "voice_authenticity": result["voice_authenticity"],
                "speech": result["speech"],
                "scam_behavior": result["scam_behavior"],
                "identity": result["identity"],
                "overall_risk": result["overall_risk"],
                "attack_patterns": result["attack_patterns"],
                "audio_quality": result["audio_quality"]
            }
            
            # Send Update
            await websocket.send_text(json.dumps(update_msg))
            
            # Send events sequentially
            for ev in events_emitted:
                await websocket.send_text(json.dumps(ev))
                
        except Exception as e:
            logger.error(f"Background analysis failed for session {session.session_id}: {e}")


@router.websocket("/ws/call/{session_id}")
async def websocket_call_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    if session_manager.active_sessions_count >= settings.MAX_ACTIVE_SESSIONS:
        await websocket.send_text(json.dumps({"type": "error", "code": "MAX_SESSIONS_REACHED"}))
        await websocket.close()
        return

    session = session_manager.create_session(session_id)
    session.add_event("CALL_STARTED", "Call tracking initialized.")
    logger.info(f"WebSocket session created. ({session.get_masked_phone()})")
    
    # Pre-allocate buffer limitations
    max_buffer_bytes = settings.MAX_AUDIO_BUFFER_SECONDS * 16000 * 2 # 16kHz, 16bit = 2 bytes per sample
    
    try:
        while True:
            # We must expect both text controls and binary streams
            message = await websocket.receive()
            
            # Text Message (Control)
            if "text" in message:
                try:
                    payload = json.loads(message["text"])
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "code": "MALFORMED_JSON",
                        "message": "Invalid JSON text sent to websocket."
                    }))
                    continue
                    
                try:
                    cmd = payload.get("type", "").lower()
                    
                    if cmd == "start":
                        caller_obj = payload.get("caller", {})
                        phone_number = caller_obj.get("phone_number")
                        session.caller_phone_number = phone_number
                        session.call_direction = caller_obj.get("call_direction", "UNKNOWN")
                        
                        logger.info(f"Session {session_id} tracking caller natively: {session.get_masked_phone()}")
                        
                        # Process caller context
                        from app.services.contact_service import contact_service
                        contact = contact_service.find_by_phone_number(phone_number)
                        
                        if contact:
                            session.add_event("KNOWN_CONTACT", f"Recognized known contact {contact.name}")
                        else:
                            session.add_event("UNKNOWN_CALLER", "Incoming call from undocumented number")
                            
                        caller_ctx_reply = {
                            "type": "caller_context",
                            "caller": {
                                "phone_number": phone_number,
                                "known_number": contact is not None,
                                "trusted_contact": contact.trusted if contact else False,
                                "name": contact.name if contact else None,
                                "relationship": contact.relationship if contact else None
                            }
                        }
                        await websocket.send_text(json.dumps(caller_ctx_reply))
                        
                    elif cmd == "verification":
                        res = payload.get("status", "NOT_AVAILABLE")
                        session.verification_status = res
                        logger.info(f"Verification challenge marked as: {res}")
                        session.add_event(f"VERIFICATION_{res}", f"Private identity verification marked as {res}")
                        
                    elif cmd == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                    elif cmd == "stop":
                        summary = {
                             "type": "session_summary",
                             "session_id": session.session_id,
                             "duration_seconds": int(time.time() - session.start_time),
                             "final_risk_score": session.current_risk,
                             "final_risk_level": session.current_risk_level,
                             "attack_patterns": session.attack_patterns
                        }
                        await websocket.send_text(json.dumps(summary))
                        break
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({"type": "error", "code": "INVALID_JSON"}))
            
            # Binary Message (Audio)
            elif "bytes" in message:
                audio_chunk = message["bytes"]
                
                if len(audio_chunk) == 0:
                    continue
                    
                if len(audio_chunk) > settings.MAX_AUDIO_CHUNK_SIZE:
                    await websocket.send_text(json.dumps({"type": "error", "code": "CHUNK_TOO_LARGE"}))
                    continue
                    
                # Format check heuristic: 16-bit PCM should have an even number of bytes
                if len(audio_chunk) % 2 != 0:
                    await websocket.send_text(json.dumps({
                        "type": "error", 
                        "code": "INVALID_AUDIO_FORMAT", 
                        "message": "Expected 16 kHz mono PCM audio."
                    }))
                    continue
                
                session.chunks_received += 1
                session.audio_buffer.extend(audio_chunk)
                
                # Trim buffer to MAX_AUDIO_BUFFER_SECONDS size rolling window
                if len(session.audio_buffer) > max_buffer_bytes:
                     excess = len(session.audio_buffer) - max_buffer_bytes
                     session.audio_buffer = session.audio_buffer[excess:]
                     
                samples_added = len(audio_chunk) / 2
                chunk_sec = samples_added / 16000.0
                session.total_audio_seconds += chunk_sec
                
                # Check session duration bounds
                if (time.time() - session.start_time) > settings.MAX_SESSION_DURATION:
                     await websocket.send_text(json.dumps({"type": "error", "code": "MAX_DURATION_EXCEEDED"}))
                     break
                
                now = time.time()
                if now - session.last_analysis_time >= settings.ANALYSIS_INTERVAL_SECONDS:
                     # Limit audio analysis to something AASIST prefers: ~4 seconds if we can, or up to 20s
                     # We'll take the entire buffer that we've rolling maintained (up to max_buffer allowed)
                     analysis_view = bytes(session.audio_buffer)
                     # Only pass up to what AASIST supports securely (or it chunks internally anyway)
                     session.last_analysis_time = now
                     
                     asyncio.create_task(analyze_background(websocket, session, analysis_view))
                     
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected linearly: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket unhandled error: {e}")
    finally:
        session_manager.close_session(session_id)
        logger.info(f"WebSocket session cleanup: {session_id}")
