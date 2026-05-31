from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

# Dummys estruturais para simulação de injeção/banco enquanto a infra não unifica
class SessionCreateRequest(BaseModel):
    patient_id: str
    doctor_id: str

class FakeSession:
    def __init__(self, session_id: str, status: str = "ACTIVE"):
        self.session_id = session_id
        self.status = status
        self.metadata = {}

# Banco em memória temporário para simulação imediata do runtime das rotas
DB_SIMULATOR: Dict[str, FakeSession] = {
    "test-session-123": FakeSession("test-session-123", "ACTIVE")
}

@router.post("/start")
async def start_session(payload: SessionCreateRequest):
    session_id = f"sess_{len(DB_SIMULATOR) + 1}"
    DB_SIMULATOR[session_id] = FakeSession(session_id, "ACTIVE")
    return {"status": "SUCCESS", "session_id": session_id}

# CORREÇÃO: Mudado de /(session_id)/transition para /{session_id}/transition
@router.post("/{session_id}/transition")
async def transition_target(session_id: str, target_data: Dict[str, Any]):
    session = DB_SIMULATOR.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    # CORREÇÃO: Alterado de '=' (atribuição) para '==' (comparação)
    if session.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Sessão em estado inválido: {session.status}")
        
    session.metadata["last_target"] = target_data.get("current_target")
    return {"status": "TRANSITION_ACCEPTED", "session_id": session_id}

# CORREÇÃO: Mudado de /{session_id]/consolidate para /{session_id}/consolidate
@router.post("/{session_id}/consolidate")
async def consolidate_session(session_id: str):
    session = DB_SIMULATOR.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    # CORREÇÃO: Lógica invertida corrigida. A sessão DEVE estar ativa para ser consolidada.
    if session.status != "ACTIVE":
        raise HTTPException(
            status_code=400, 
            detail=f"A sessão não pode ser consolidada pois seu estado atual é: {session.status}"
        )
        
    session.status = "CONSOLIDATED"
    return {
        "status": "CONSOLIDATED", 
        "session_id": session_id,
        "metrics_summary": {"mean_deviation_deg": 1.4, "gaze_stability_score": 92.5}
    }

# CORREÇÃO: Mudado de / session_id]/abort para /{session_id}/abort
@router.post("/{session_id}/abort")
async def abort_session(session_id: str):
    session = DB_SIMULATOR.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
        
    session.status = "ABORTED"
    return {"status": "ABORTED", "session_id": session_id}
