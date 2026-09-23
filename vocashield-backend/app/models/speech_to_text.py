import logging
import torch
import numpy as np
import time
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

class SpeechToText:
    def __init__(self):
        self.device_setting = settings.WHISPER_DEVICE
        if self.device_setting == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = self.device_setting
            
        self.model_name = settings.WHISPER_MODEL
        self.model = None
        self.is_loaded = False

    def load_model(self):
        if self.is_loaded:
            return
            
        logger.info(f"Loading Whisper transcription model ({self.model_name})...")
        logger.info(f"Target Device: {self.device.upper()}")
        
        try:
            import whisper
            # download_root can be specified, but we'll use default cache
            self.model = whisper.load_model(self.model_name, device=self.device)
            self.is_loaded = True
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            raise RuntimeError(f"Whisper model initialization failed: {str(e)}")

    def transcribe(self, waveform: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        if not self.is_loaded:
            self.load_model()
            
        if sample_rate != 16000:
            raise ValueError(f"Whisper requires 16kHz audio, got {sample_rate}Hz")
            
        # Whisper requires float32 between -1 and +1
        # It's robust enough, but we should ensure it's correct.
        if waveform.dtype != np.float32:
            waveform = waveform.astype(np.float32)
            
        if len(waveform) == 0:
            return {
                "text": "",
                "language": "en",
                "duration_seconds": 0.0
            }

        duration_seconds = len(waveform) / sample_rate
        
        try:
            # transcribe
            logger.debug("Running Whisper inference...")
            result = self.model.transcribe(waveform, fp16=(self.device == "cuda"))
            
            text = result.get("text", "").strip()
            language = result.get("language", "en")
            
            logger.info(f"[Whisper] Language: {language}")
            logger.info(f"[Whisper] Transcript: {text}")
            
            return {
                "text": text,
                "language": language,
                "duration_seconds": round(duration_seconds, 2)
            }
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return {
                "text": "",
                "language": "en",
                "duration_seconds": round(duration_seconds, 2),
                "error": str(e)
            }

# Singleton instance
transcriber = SpeechToText()
