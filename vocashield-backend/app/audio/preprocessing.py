import io
import librosa
import soundfile as sf
import numpy as np
import logging

logger = logging.getLogger(__name__)

class AudioProcessingError(Exception):
    pass

MAX_DURATION_SECONDS = 300 # 5 minutes

def validate_audio_file(filename: str, content_type: str) -> bool:
    """Basic validation for audio files."""
    allowed_extensions = {".wav", ".mp3", ".m4a"}
    has_valid_ext = any(filename.lower().endswith(ext) for ext in allowed_extensions)
    return has_valid_ext

def process_audio(file_bytes: bytes) -> dict:
    """
    Process audio bytes according to pipeline:
    1. Load safely
    2. Convert to Mono
    3. Resample to 16000Hz
    4. Float32 conversion
    5. Safe normalization
    6. Basic VAD (trimming silence)
    """
    TARGET_SR = 16000
    
    if len(file_bytes) == 0:
        raise AudioProcessingError("Empty audio file.")
        
    try:
        # soundfile is fast and reliable for valid wav, but might fail on mp3/m4a depending on installed backends. 
        # librosa handles more through soundfile/audioread.
        with sf.SoundFile(io.BytesIO(file_bytes)) as s_file:
            original_sr = s_file.samplerate
            original_channels = s_file.channels
            frames = s_file.frames
            
            original_duration = frames / original_sr if original_sr > 0 else 0
            
            if original_duration == 0:
                raise AudioProcessingError("Audio file has no duration.")
                
            if original_duration > MAX_DURATION_SECONDS:
                raise AudioProcessingError(f"Audio exceeds maximum duration of {MAX_DURATION_SECONDS} seconds.")
                
            # We can load it now
            s_file.seek(0)
            waveform_raw = s_file.read(dtype='float32')
            
    except Exception as e:
        if isinstance(e, AudioProcessingError):
            raise
        # Fallback to librosa if soundfile fails (e.g. mp3 sometimes)
        try:
            waveform_raw, original_sr = librosa.load(io.BytesIO(file_bytes), sr=None, mono=False)
            original_duration = librosa.get_duration(y=waveform_raw, sr=original_sr)
            if original_duration == 0:
                raise AudioProcessingError("Audio file has no duration.")
            if original_duration > MAX_DURATION_SECONDS:
                raise AudioProcessingError(f"Audio exceeds maximum duration of {MAX_DURATION_SECONDS} seconds.")
            original_channels = 1 if waveform_raw.ndim == 1 else waveform_raw.shape[0]
            
            if waveform_raw.ndim > 1:
                # Transpose for consistent handling (samples, channels)
                waveform_raw = waveform_raw.T
        except Exception as e2:
            raise AudioProcessingError(f"Corrupted or unsupported audio format. Details: {str(e2)}")

    # Convert to Mono
    if waveform_raw.ndim > 1 and waveform_raw.shape[1] > 1:
        # average across channels. librosa.to_mono expects (channels, samples)
        # waveform_raw is (samples, channels) due to sf.read
        waveform_mono = librosa.to_mono(waveform_raw.T)
    elif waveform_raw.ndim > 1 and waveform_raw.shape[1] == 1:
        waveform_mono = waveform_raw[:, 0]
    else:
        waveform_mono = waveform_raw
        
    processed_channels = 1
    
    # Resample to 16000Hz (Float32 is default in librosa.resample)
    if original_sr != TARGET_SR:
        waveform_target = librosa.resample(y=waveform_mono, orig_sr=original_sr, target_sr=TARGET_SR)
    else:
        waveform_target = waveform_mono

    # Float32 conversion (ensure)
    waveform_target = waveform_target.astype(np.float32)
    
    # Normalize safely
    max_amp = np.max(np.abs(waveform_target))
    if max_amp > 0:
        waveform_target = waveform_target / max_amp
        
    # Basic VAD: Trim leading and trailing silence
    # We do not aggressively trim internal silence to preserve forensic characteristics
    waveform_trimmed, index = librosa.effects.trim(waveform_target, top_db=30)
    
    # Meaningful speech check
    if len(waveform_trimmed) == 0 or np.max(np.abs(waveform_trimmed)) < 1e-3:
        raise AudioProcessingError("Audio contains no meaningful speech or is completely silent.")

    duration_seconds = len(waveform_trimmed) / TARGET_SR
    
    return {
        "waveform": waveform_trimmed, # For internal use (ML model)
        "processed_sample_rate": TARGET_SR,
        "duration_seconds": round(duration_seconds, 2),
        "original_sample_rate": original_sr,
        "original_channels": original_channels,
        "processed_channels": processed_channels
    }
