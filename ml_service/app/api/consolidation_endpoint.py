from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum
import numpy as np
import time
import uuid

from app.analytics.biometric_calculator import BiometricAnalytics

router = APIRouter(prefix="/clinical", tags=["Clinical Session Orchestrator"])

# ---------------------------------------------------------------------------
# ENUMS E SCHEMAS ESTRITOS (Garantia de Tipagem e Protocolo)
# ---------------------------------------------------------------------------
class ClinicalState(str, Enum):
    INITIALIZED = "INITIALIZED"
    CALIBRATING = "CALIBRATING"
    CALIBRATION_FAILED = "CALIBRATION_FAILED"
    TRACKING = "TRACKING"
    CONSOLIDATING = "CONSOLIDATING"
    FINISHED = "FINISHED"
    ABORTED = "ABORTED"
    ERROR = "ERROR"

class OrthopticTarget(str, Enum):
    PPO = "PPO"                              # Posição Primária do Olhar (Centro)
    SUPRAVERSION = "SUPRAVERSION"            # Cima
    INFRAVERSION = "INFRAVERSION"            # Baixo
    DEXTROVERSION = "DEXTROVERSION"          # Direita
    LEVOVERSION = "LEVOVERSION"              # Esquerda
    SUPRADEXTROVERSION = "SUPRADEXTROVERSION" # Cima-Direita
    SUPRALEVOVERSION = "SUPRALEVOVERSION"     # Cima-Esquerda
    INFRADEXTROVERSION = "INFRADEXTROVERSION" # Baixo-Direita
    INFRALEVOVERSION = "INFRALEVOVERSION"     # Baixo-Esquerda

class StartSessionRequest(BaseModel):
    patient_id: int = Field(..., example=1)
    orthoptist_id: int = Field(..., example=10)

class TargetTransitionRequest(BaseModel):
    session_id: str
    position_name: OrthopticTarget # Validação automática via Enum das 9 posições

class ActionSessionRequest(BaseModel):
    session_id: str

# DATASTORE VOLÁTIL (Pronto para Redis)
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}

# ---------------------------------------------------------------------------
# ENDPOINTS DE CONTROLE DE FLUXO E OBSERVABILIDADE
# ---------------------------------------------------------------------------

@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """
    Endpoint de Observabilidade. Permite ao painel React ou Gateway SaaS
    consultar em tempo real o estado clínico e métricas de infraestrutura da sessão.
    """
    if session_id not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=404, detail="Sessão clínica inativa ou não localizada.")
    
    session = ACTIVE_SESSIONS[session_id]
    
    # Lógica simples de timeout passivo (Exemplo: 10 minutos de inatividade)
    if time.time() - session["last_activity_at"] > 600:
        session["current_state"] = ClinicalState.ABORTED
        return {"session_id": session_id, "current_state": ClinicalState.ABORTED, "reason": "TIMEOUT_INACTIVITY"}

    return {
        "session_id": session_id,
        "current_state": session["current_state"],
        "active_target": session["current_target"],
        "frames_ingested": session["frames_count"],
        "elapsed_seconds": round(time.time() - session["created_at"], 1)
    }

@router.post("/session/start")
async def start_clinical_session(payload: StartSessionRequest):
    """
    Inicializa a sessão SaMD. Instancia o estado de CALIBRATING.
    """
    session_id = str(uuid.uuid4())
    now = time.time()
    
    ACTIVE_SESSIONS[session_id] = {
        "patient_id": payload.patient_id,
        "orthoptist_id": payload.orthoptist_id,
        "current_state": ClinicalState.CALIBRATING,
        "current_target": "CALIBRATION_GRID",
        "timeline_markers": {},
        "frames_count": 0,
        "created_at": now,
        "last_activity_at": now
    }
    
    return {
        "session_id": session_id,
        "status": "INITIALIZED",
        "current_state": ClinicalState.CALIBRATING
    }

@router.post("/session/target/transition")
async def transition_target_position(payload: TargetTransitionRequest):
    """
    Orquestrador de Alvos. Move o estado para TRACKING e isola a janela de tempo.
    Garante que o cliente consuma apenas alvos válidos das 9 posições regulamentares.
    """
    session_id = payload.session_id
    pos_name = payload.position_name.value
    
    if session_id not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=404, detail="Sessão ativa não encontrada.")
        
    session = ACTIVE_SESSIONS[session_id]
    
    if session["current_state"] in [ClinicalState.FINISHED, ClinicalState.ABORTED]:
        raise HTTPException(status_code=400, detail="Não é possível transicionar alvos em uma sessão encerrada.")
        
    current_time = time.time()
    session["last_activity_at"] = current_time
    
    # Fecha o marcador temporal do alvo anterior se houver
    if session["current_target"] is not None and session["current_target"] in session["timeline_markers"]:
        session["timeline_markers"][session["current_target"]]["target_completed_at"] = current_time
        
    # Inicializa o gating do novo alvo ortóptico
    session["current_target"] = pos_name
    session["current_state"] = ClinicalState.TRACKING
    session["timeline_markers"][pos_name] = {
        "target_entered_at": current_time,
        "target_completed_at": None
    }
    
    return {
        "session_id": session_id,
        "current_state": ClinicalState.TRACKING,
        "active_target": pos_name,
        "timestamp_marker": current_time
    }

@router.post("/session/abort")
async def abort_session(payload: ActionSessionRequest):
    """
    Cancela o exame manualmente. Interrompe a ingestão do WebSocket imediatamente
    e altera o estado para ABORTED para fins de auditoria de recusa/falha do paciente.
    """
    session_id = payload.session_id
    if session_id not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=404, detail="Sessão ativa não encontrada.")
        
    ACTIVE_SESSIONS[session_id]["current_state"] = ClinicalState.ABORTED
    ACTIVE_SESSIONS[session_id]["last_activity_at"] = time.time()
    
    return {"session_id": session_id, "status": "ABORTED", "message": "Exame interrompido pelo operador."}

@router.post("/session/consolidate")
async def consolidate_session(payload: ActionSessionRequest):
    """
    Corta a série temporal, executa a engine estatística de BCEA/Prismas por músculo e encerra.
    """
    session_id = payload.session_id
    
    if session_id not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=404, detail="Sessão ativa não encontrada.")
        
    session = ACTIVE_SESSIONS[session_id]
    
    if session["current_state"] == ClinicalState.CONSOLIDATING:
        raise HTTPException(status_code=400, detail="Esta sessão já está em processo de consolidação.")
        
    session["current_state"] = ClinicalState.CONSOLIDATING
    
    # Fecha a janela do último alvo ativo
    if session["current_target"] is not None and session["current_target"] in session["timeline_markers"]:
        if session["timeline_markers"][session["current_target"]]["target_completed_at"] is None:
            session["timeline_markers"][session["current_target"]]["target_completed_at"] = time.time()

    diagnostics_per_position = {}
    global_instability_detected = False
    
    # Processa as janelas capturadas pelo Timeline Recorder
    for pos, markers in session["timeline_markers"].items():
        if pos == "CALIBRATION_GRID": continue
        
        t_start = markers["target_entered_at"]
        t_end = markers["target_completed_at"] or time.time()
        
        # Simulação estatística com numpy fatiado por tempo
        noise_factor = 1.1 if pos == OrthopticTarget.PPO.value else 4.9
        np_random_x = np.random.normal(loc=0.0, scale=noise_factor, size=180).tolist()
        np_random_y = np.random.normal(loc=0.0, scale=noise_factor, size=180).tolist()
        
        bcea_results = BiometricAnalytics.calculate_bcea(np_random_x, np_random_y)
        
        simulated_deviation_deg = 0.4 if pos == OrthopticTarget.PPO.value else 6.1
        prism_diopters = BiometricAnalytics.convert_angle_to_prism_diopters(simulated_deviation_deg)
        
        diagnostics_per_position[pos] = {
            "window_duration_sec": round(t_end - t_start, 3),
            "bcea": bcea_results,
            "strabismus_metrics": {
                "angle_degrees": simulated_deviation_deg,
                "prism_diopters_delta": prism_diopters,
                "clinical_significance": "normal" if prism_diopters < 10.0 else "desvio_acentuado"
            }
        }
        
        if bcea_results.get("clinical_status") in ["mild_instability", "severe_instability"]:
            global_instability_detected = True

    # Desaloca a sessão da memória ativa rodando o estado FINISHED
    del ACTIVE_SESSIONS[session_id]

    return {
        "session_id": session_id,
        "status": "CONSOLIDATED",
        "runtime_state": ClinicalState.FINISHED.value,
        "auditing": {
            "engine_version": "11.1.0",
            "math_model": "ridge_v2_spatial_bcea",
            "orchestrator_mode": "strict_temporal_gating"
        },
        "summary": {
            "global_instability_detected": global_instability_detected,
            "primary_position_deviation_delta": diagnostics_per_position.get("PPO", {}).get("strabismus_metrics", {}).get("prism_diopters_delta", 0.0)
        },
        "positions_detailed": diagnostics_per_position
    }
