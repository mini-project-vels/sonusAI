import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "VocaShield AI Phase 1"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: Union[str, List[str]] = ["*"]
    ENVIRONMENT: str = "development"
    DEEPFAKE_MODEL_PATH: str = "models/deepfake/AASIST.pth"
    WHISPER_MODEL: str = "base"
    WHISPER_DEVICE: str = "auto"
    
    # WebSocket Configuration
    ANALYSIS_INTERVAL_SECONDS: float = 2.0
    MAX_CONCURRENT_ANALYSES: int = 2
    MAX_AUDIO_CHUNK_SIZE: int = 1024 * 1024  # 1 MB
    MAX_SESSION_DURATION: int = 3600
    MAX_ACTIVE_SESSIONS: int = 100
    MAX_AUDIO_BUFFER_SECONDS: int = 60
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
