import logging
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import engine, Base
from app.session.session_models import ExamSession, GazeTelemetry

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SaMDEngine")

# --- Validador de Qualidade (Sprint 1.1) ---
class PreExamValidator:
    def validate(self, landmarks, pose, frame):
        # Cálculo de luminância média para iluminação
        gray = np.mean(frame) if frame is not None else 0
        lighting_score = 1.0 if 100 <= gray <= 180 else (0.6 if 50 <= gray < 100 else 0.2)
        
        checks = {
            "face_detected": len(landmarks) > 0,
            "pose_ok": abs(pose.get('pitch', 0)) < 10 and abs(pose.get('yaw', 0)) < 10 and abs(pose.get('roll', 0)) < 15,
            "lighting_ok": 0.5 < lighting_score <= 1.0,
            "confidence_ok": True
        }
        
        score = ((1.0 if checks["face_detected"] else 0.0) * 0.3 + 
                 (1.0 if checks["pose_ok"] else 0.0) * 0.3 + 
                 (lighting_score) * 0.2 + 0.2) * 100
        
        return {
            "status": "READY_TO_START" if all(checks.values()) else "WAITING_FOR_ENVIRONMENT",
            "quality_score": round(score, 1),
            "checks": checks
        }

validator = PreExamValidator()

# --- Ciclo de Vida ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("⚙️ Inicializando migrações e criando tabelas no SQLite assíncrono...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Tabelas ortópticas sincronizadas com sucesso.")
    yield
    logger.info("🔌 Encerrando Engine...")
    await engine.dispose()

app = FastAPI(
    title="Precision Vision Engine",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "engine": "active"}

# --- Estrutura de Envio do WebSocket (Para referência) ---
"""
# Dentro do seu gateway WebSocket (ex: /ws/telemetry), o envio agora deve ser:
pre_exam_data = validator.validate(landmarks, pose, frame)

payload = {
    "telemetry": {
        "gaze_x": gaze_x,
        "gaze_y": gaze_y,
        "confidence_score": conf,
        "latency_sec": lat
    },
    "pre_exam": pre_exam_data
}
await websocket.send_json(payload)
"""
