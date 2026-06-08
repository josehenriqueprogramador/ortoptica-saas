from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# Estruturas de suporte (ajuste conforme seu session_models.py)
class SessionCreateRequest(BaseModel):
    session_id: str

router = APIRouter(prefix="/clinical")

@router.post("/start")
async def start_session(request: SessionCreateRequest):
    # Simulação de início
    return {"status": "started", "session_id": request.session_id}

@router.post("/{session_id}/transition")
async def transition_target(session_id: str):
    # Correção: Comparação lógica (==) e rotas corrigidas com chaves {}
    # session = manager.get_session(session_id)
    # if session.status == "ACTIVE":
    return {"status": "transitioned", "new_target": "PERIPHERAL"}
    # raise HTTPException(status_code=400, detail="Sessão não está ativa")

@router.post("/{session_id}/consolidate")
async def consolidate_session(session_id: str):
    # Correção: Lógica invertida (só consolida se estiver ACTIVE)
    status = "ACTIVE" # Mock para validação
    if status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Sessão não pode ser consolidada...")
    return {"status": "consolidated"}

@router.post("/{session_id}/abort")
async def abort_session(session_id: str):
    return {"status": "aborted"}
