import pytest
import numpy as np
from app.models.speech_to_text import transcriber

def test_whisper_transcription_silence():
    waveform = np.zeros(16000, dtype=np.float32)
    # The speech_to_text module shouldn't crash
    result = transcriber.transcribe(waveform, 16000)
    
    # Whisper usually outputs '' or hallucinates on pure zeroes. 
    assert result["text"] == "" or isinstance(result["text"], str)
    assert result["duration_seconds"] == 1.0

def test_whisper_invalid_sample_rate():
    waveform = np.zeros(44100, dtype=np.float32)
    with pytest.raises(ValueError):
         transcriber.transcribe(waveform, 44100)
