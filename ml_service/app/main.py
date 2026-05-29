import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import engine, Base
# Importações forçadas dos modelos para registro no ciclo do Metadata
from app.session.session_models import ExamSession, GazeTelemetry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SaMDEngine")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executado no Startup do Container
    logger.info("⚙️ Inicializando migrações e criando tabelas no SQLite assíncrono...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Tabelas ortópticas sincronizadas com sucesso.")
    yield
    # Executado no Shutdown do Container
    logger.info("🔌 Encerrando Engine de Banco de Dados...")
    await engine.dispose()

app = FastAPI(
    title="OrtoPtica SaMD Engine",
    description="Motor Craniométrico e Rastreamento de Olhar Baseado em Visão Computacional",
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

# Rota de verificação de integridade operacional
@app.get("/health")
async def health_check():
    return {"status": "healthy", "engine": "active", "version": "1.0.0"}

# Os roteadores de API (HTTP) e Gateways (WebSockets) injetados previamente 
# passam a operar sob a proteção deste ciclo lifespan unificado.
