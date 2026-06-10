from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.session.session_models import ExaminationSession
from database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/clinical")

class SessionCreateRequest(BaseModel):
    session_id: str

@router.post("/start")
async def start_session(request: SessionCreateRequest, db: AsyncSession = Depends(get_db)):
    return {"status": "started", "session_id": request.session_id}

@router.post("/{session_id}/transition")
async def transition_target(session_id: str, db: AsyncSession = Depends(get_db)):
    query = select(ExaminationSession).where(ExaminationSession.session_id == session_id)
    result = await db.execute(query)
    session = result.scalars().first()

    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada no banco.")

    if session.status != "ACTIVE":
         raise HTTPException(status_code=400, detail="Transição negada: Sessão não está ativa.")

    return {"status": "transitioned", "new_target": "PERIPHERAL"}

@router.post("/{session_id}/consolidate")
async def consolidate_session(session_id: str, db: AsyncSession = Depends(get_db)):
    query = select(ExaminationSession).where(ExaminationSession.session_id == session_id)
    result = await db.execute(query)
    session = result.scalars().first()

    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")

    if session.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Sessão não pode ser consolidada. O status atual não é ACTIVE.")

    try:
        session.status = "CONSOLIDATED"
        await db.commit()
        return {"status": "consolidated", "message": "Biometria processada e salva com sucesso."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao consolidar no banco: {str(e)}")

@router.post("/{session_id}/abort")
async def abort_session(session_id: str, db: AsyncSession = Depends(get_db)):
    return {"status": "aborted"}
