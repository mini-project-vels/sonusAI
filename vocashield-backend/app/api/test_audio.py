import os
import json
import logging
import soundfile as sf
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.api.websocket import run_synchronous_pipeline # We can reuse the sync pipeline from websocket
from app.api.analysis import parse_audio_to_waveform # Assuming this exists or similar

router = APIRouter()
logger = logging.getLogger(__name__)

TEST_AUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "test_audio"))
META_PATH = os.path.join(TEST_AUDIO_DIR, "metadata.json")

def get_metadata() -> Dict[str, Any]:
    if not os.path.exists(META_PATH):
        return {"samples": []}
    with open(META_PATH, "r") as f:
        return json.load(f)

@router.get("/test-audio")
async def list_test_audio():
    metadata = get_metadata()
    samples = []
    
    for s in metadata.get("samples", []):
        cat = s["category"]
        filepath = os.path.join(TEST_AUDIO_DIR, cat, s["filename"])
        
        # Fast duration check
        dur = 0.0
        if os.path.exists(filepath):
            try:
                info = sf.info(filepath)
                dur = round(info.frames / info.samplerate, 2)
            except:
                pass
                
        samples.append({
            "id": s["id"],
            "filename": s["filename"],
            "category": cat,
            "display_name": f"{cat.capitalize()} Sample {s['id'].split('_')[-1]}",
            "duration_seconds": dur
        })
        
    return {"samples": samples}

@router.get("/test-audio/{sample_id}/audio")
async def stream_test_audio(sample_id: str):
    metadata = get_metadata()
    for s in metadata.get("samples", []):
        if s["id"] == sample_id:
            filepath = os.path.join(TEST_AUDIO_DIR, s["category"], s["filename"])
            if not os.path.exists(filepath):
                raise HTTPException(status_code=404, detail="Audio file not found")
            return FileResponse(filepath, media_type="audio/wav")
            
    raise HTTPException(status_code=404, detail="Sample not found")

@router.post("/test-audio/{sample_id}/analyze")
async def analyze_test_audio(sample_id: str):
    metadata = get_metadata()
    sample = None
    for s in metadata.get("samples", []):
        if s["id"] == sample_id:
            sample = s
            break
            
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
        
    filepath = os.path.join(TEST_AUDIO_DIR, sample["category"], sample["filename"])
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Audio file not found")
        
    # Read waveform natively
    data, sr = sf.read(filepath, dtype='float32')
    
    # Run the existing synchronous pipeline
    try:
        # Generate random session for isolation
        import uuid
        session_id = str(uuid.uuid4())
        
        # We need to use run_synchronous_pipeline
        # Current transcript is empty
        result = run_synchronous_pipeline(session_id, data, "")
        
        # Match standard POST /api/v1/analyze structure
        response = {
            "success": True,
            "analysis_id": session_id,
            "processing_time_ms": result["performance"]["total_analysis_ms"],
            "audio": result["audio_quality"],
            "deepfake": {
                "fake_probability": result["voice_authenticity"]["fake_probability"],
                "prediction": "FAKE" if result["voice_authenticity"]["label"] == "LIKELY_AI_GENERATED" else "REAL",
            },
            "transcription": result["speech"],
            "scam_analysis": {
                "scam_behavior_score": result["scam_behavior"]["score"],
                "signals": result["scam_behavior"]["signals"]
            },
            "risk_assessment": {
                "identity": result["identity"],
                "overall_risk_score": result["overall_risk"]["score"],
                "risk_level": result["overall_risk"]["level"],
                "attack_patterns": result["attack_patterns"],
                "recommendations": result.get("recommendations", [])
            },
            "test_sample": {
                "id": sample["id"],
                "ground_truth": sample["ground_truth"],
                "source": sample["source"]
            }
        }
        return response
        
    except Exception as e:
        logger.error(f"Test analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
