import pytest
import io
from fastapi.testclient import TestClient
from app.main import app
import numpy as np
import scipy.io.wavfile as wavfile

client = TestClient(app)

def generate_wav_bytes(sample_rate: int, channels: int, duration: float, amplitude: float = 0.5) -> bytes:
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    signal = np.sin(440 * 2 * np.pi * t) * amplitude
    signal_scaled = np.int16(signal * 32767)
    if channels > 1:
        signal_scaled = np.column_stack([signal_scaled] * channels)
    buf = io.BytesIO()
    wavfile.write(buf, sample_rate, signal_scaled)
    return buf.getvalue()

def test_api_analyze_audio_success():
    wav_bytes = generate_wav_bytes(44100, 2, 2.5) # 2.5s stereo @ 44.1kHz
    
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("test_stereo.wav", wav_bytes, "audio/wav")}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert "analysis_id" in data
    
    assert "processing_time_ms" in data
    assert "transcription" in data
    assert "scam_analysis" in data
    assert "signals" in data["scam_analysis"]
    assert "risk_assessment" in data
    assert "overall_risk_score" in data["risk_assessment"]
    
    audio_meta = data["audio"]
    assert audio_meta["original_sample_rate"] == 44100
    assert audio_meta["processed_sample_rate"] == 16000
    assert audio_meta["original_channels"] == 2
    assert audio_meta["processed_channels"] == 1
    assert data["deepfake"] is not None # Actually processed real AASIST

def test_api_analyze_audio_silence():
    # complete silence
    t = np.linspace(0, 1.0, 16000, False)
    signal = np.zeros_like(t)
    buf = io.BytesIO()
    wavfile.write(buf, 16000, np.int16(signal))
    wav_bytes = buf.getvalue()
    
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("silence.wav", wav_bytes, "audio/wav")}
    )
    
    assert response.status_code == 400
    assert "no meaningful speech" in response.json()["detail"].lower()
