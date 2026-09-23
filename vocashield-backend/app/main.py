import logging
from app.api import contacts
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.websocket import router as websocket_router
from app.core.config import settings
from app.api import analysis
from dotenv import load_dotenv

load_dotenv()

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VocaShield AI - Risk Matrix",
    description="Backend engine for deepfake detection, scam analysis, and integrated caller context matrix natively designed for Phase 7 Android Integration.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
cors_origins = settings.CORS_ORIGINS
if isinstance(cors_origins, str):
    cors_origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Includes API Endpoints
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(contacts.router, prefix=settings.API_V1_STR + "/contacts")
app.include_router(websocket_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "vocashield-backend",
        "phase": 1
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
