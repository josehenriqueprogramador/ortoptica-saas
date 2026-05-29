from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
import datetime

from database import get_db
from app.session.session_models import ClinicalSession
from app.session.session_manager import session_manager
from app.analytics.biometric_calculator import BiometricCalculator

router = APIRouter(prefix="/api/clinical", tags=["Orquestração Clínica"])

# --- Schemas de Validação (Pydantic) ---
class SessionCreateRequest(BaseModel):
    session_id: str = Field(..., example="8f9g7h6j-1234-abcd-efgh-1234567890ab")

class SessionResponse(BaseModel):
    session_id: str
    status: str
    created_at: datetime.datetime
    bcea_score: float | None

    class Config:
        from_attributes = True

class TransitionRequest(BaseModel):
    target_label: str = Field(..., example="UP_RIGHT_STRABISMUS_CHECK")


# --- Rotas do Ciclo de Vida HTTP ---

@router.post("/start", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(payload: SessionCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Inicializa formalmente o estado do exame médico no banco de dados e
    aloca uma instância em memória RAM para o streaming de alta frequência.
    """
    query = select(ClinicalSession).where(ClinicalSession.id == payload.session_id)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Identificador de sessão já ativo ou utilizado.")

    # 1. Cria o registro persistente de auditoria clínica
    new_session = ClinicalSession(id=payload.session_id, status="ACTIVE")
    db.add(new_session)
    
    # 2. Inicializa o buffer volátil em memória RAM para o WebSocket
    session_manager.start_session(payload.session_id)

    await db.commit()
    await db.refresh(new_session)
    return SessionResponse(
        session_id=new_session.id,
        status=new_session.status,
        created_at=new_session.created_at,
        bcea_score=new_session.bcea_score
    )

@router.post("/{session_id}/transition", status_code=status.HTTP_200_OK)
async def transition_target(session_id: str, payload: TransitionRequest, db: AsyncSession = Depends(get_db)):
    """
    Sincroniza o movimento do estímulo visual feito pelo médico.
    Atualiza o runtime em memória para segmentar corretamente os vetores de foveação.
    """
    query = select(ClinicalSession).where(ClinicalSession.id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Sessão clínica não localizada.")
    if session.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Incapaz de transicionar. Sessão encontra-se {session.status}.")

    # Intercepta a sessão em memória e altera a marcação anatômica do alvo atual
    runtime = session_manager.get_session(session_id)
    if runtime:
        runtime.update_target(payload.target_label)
        print(f"🔄 [RAM Sync] Sessão {session_id} chaveada cirurgicamente para o alvo: {payload.target_label}")
    else:
        print(f"⚠️ Alerta: Requisição de transição recebida para sessão {session_id} sem runtime ativo em RAM.")

    return {"status": "TARGET_TRANSITION_ACKNOWLEDGED", "current_target": payload.target_label}

@router.post("/{session_id}/consolidate", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def consolidate_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """
    Descarrega o buffer de telemetria da memória RAM para o banco físico em bloco,
    executa o motor analítico de BCEA e encerra o ciclo de vida do exame.
    """
    query = select(ClinicalSession).where(ClinicalSession.id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Sessão clínica não localizada.")
    if session.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Sessão não pode ser consolidada pois está {session.status}.")

    runtime = session_manager.get_session(session_id)
    if runtime:
        # 1. Executa o bulk insert assíncrono de todos os pontos de olhar coletados
        await runtime.flush_to_database(db)
        # 2. Desaloca os buffers de memória RAM para prevenir vazamentos
        session_manager.close_session(session_id)

    # 3. Executa o cálculo estatístico sobre os pontos consolidados no banco
    calculated_bcea = await BiometricCalculator.compute_session_bcea(session_id, db)

    session.status = "CONSOLIDATED"
    session.bcea_score = calculated_bcea
    
    await db.commit()
    await db.refresh(session)
    return SessionResponse(
        session_id=session.id,
        status=session.status,
        created_at=session.created_at,
        bcea_score=session.bcea_score
    )

@router.post("/{session_id}/abort", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def abort_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """
    Cancela o exame imediatamente, limpando os buffers em memória RAM e descartando dados parciais.
    """
    query = select(ClinicalSession).where(ClinicalSession.id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Sessão clínica não localizada.")

    # Limpa a sessão da RAM imediatamente sem efetuar o flush
    session_manager.close_session(session_id)

    session.status = "ABORTED"
    await db.commit()
    await db.refresh(session)
    return SessionResponse(
        session_id=session.id,
        status=session.status,
        created_at=session.created_at,
        bcea_score=session.bcea_score
    )
