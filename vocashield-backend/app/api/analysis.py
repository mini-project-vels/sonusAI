import uuid
import logging
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form
from app.schemas.analysis import AnalysisResponse, AudioMetadata, DeepfakePrediction, TranscriptionResponse, ScamAnalysisResponse, RiskAssessmentResponse
from app.audio.preprocessing import validate_audio_file, process_audio, AudioProcessingError
from app.models.deepfake_detector import detector
from app.models.speech_to_text import transcriber
from app.engines.scam_signal_engine import signal_engine
from app.engines.risk_engine import risk_engine
from app.engines.attack_pattern_engine import attack_pattern_engine
from app.engines.verification_engine import verification_engine

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit for phase 1

@router.get("/model/status")
def model_status():
    is_loaded = detector.is_loaded
    device = detector.device.type
    return {
        "model": "AASIST",
        "loaded": is_loaded,
        "device": device,
        "checkpoint": detector.model_path,
        "sample_rate": detector.sample_rate,
        "samples_per_window": detector.expected_length
    }

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_audio(
    file: UploadFile = File(...),
    context_payload: str = Form(None)
):
    # Parse Context
    import json
    context_data = {}
    if context_payload:
        try:
            context_data = json.loads(context_payload)
        except Exception as e:
            logger.warning(f"Failed to parse context_payload: {e}")

    if not validate_audio_file(file.filename, file.content_type):
        logger.warning(f"Invalid file format rejected: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload WAV, MP3, or M4A."
        )
        
    try:
        t0 = time.time()
        
        # Read file contents
        content = await file.read()
        file_size = len(content)
        
        if file_size == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty.")
            
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size is {MAX_FILE_SIZE / (1024 * 1024)}MB"
            )
            
        logger.info(f"Processing audio file: {file.filename} (Size: {file_size} bytes)")
        
        try:
            # Preprocessing implementation
            t_pre = time.time()
            audio_info = process_audio(content)
            time_pre = int((time.time() - t_pre) * 1000)
        except AudioProcessingError as e:
            logger.warning(f"Audio processing failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
            
        # Deepfake analysis
        try:
            t_aasist = time.time()
            detection_results = detector.predict(audio_info["waveform"], audio_info["processed_sample_rate"])
            time_aasist = int((time.time() - t_aasist) * 1000)
        except Exception as e:
            logger.error(f"Deepfake detector failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Deepfake model error: {str(e)}"
            )
            
        # Transcription execution
        t_whisper = time.time()
        whisper_results = transcriber.transcribe(audio_info["waveform"], audio_info["processed_sample_rate"])
        time_whisper = int((time.time() - t_whisper) * 1000)
        
        # Scam analysis logic
        t_scam = time.time()
        scam_results = signal_engine.analyze(whisper_results["text"])
        time_scam = int((time.time() - t_scam) * 1000)
        
        # Phase 4 Risk Engines
        risk_metrics = risk_engine.calculate_risk(detection_results, scam_results, context_data)
        attack_patterns = attack_pattern_engine.classify(risk_metrics, scam_results, context_data)
        recommendations = verification_engine.generate_recommendations(risk_metrics, attack_patterns, scam_results)
        
        analysis_id = str(uuid.uuid4())
        
        # Audio metadata mapping
        audio_meta = {
            "duration_seconds": audio_info["duration_seconds"],
            "original_sample_rate": audio_info["original_sample_rate"],
            "processed_sample_rate": audio_info["processed_sample_rate"],
            "original_channels": audio_info["original_channels"],
            "processed_channels": audio_info["processed_channels"]
        }
        
        total_time_ms = int((time.time() - t0) * 1000)
        logger.info(f"Pipeline complete in {total_time_ms}ms (Pre: {time_pre}, Deepfake: {time_aasist}, Whisper: {time_whisper}, Scam: {time_scam})")
        
        return AnalysisResponse(
            success=True,
            analysis_id=analysis_id,
            processing_time_ms=total_time_ms,
            audio=AudioMetadata(**audio_meta),
            deepfake=DeepfakePrediction(**detection_results),
            transcription=TranscriptionResponse(
                text=whisper_results["text"],
                language=whisper_results["language"]
            ),
            scam_analysis=ScamAnalysisResponse(**scam_results),
            risk_assessment=RiskAssessmentResponse(
                voice_risk=risk_metrics["voice_risk"],
                scam_behavior_risk=risk_metrics["scam_behavior_risk"],
                context_risk=risk_metrics["context_risk"],
                identity=risk_metrics["identity"],
                overall_risk_score=risk_metrics["overall_risk_score"],
                risk_level=risk_metrics["risk_level"],
                risk_factors=risk_metrics["risk_factors"],
                attack_patterns=attack_patterns,
                recommendations=recommendations
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the audio file."
        )
