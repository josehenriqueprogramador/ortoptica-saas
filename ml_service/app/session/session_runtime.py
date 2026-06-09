import time
from app.websocket.websocket_manager import manager
from app.session.session_models import TelemetryPacket

async def process_and_broadcast(session_id: str, result: dict):
    """
    Padroniza os dados de telemetria e transmite para os clientes conectados.
    """
    try:
        # Criação do pacote validado pelo modelo
        packet = TelemetryPacket(
            session_id=session_id,
            tracking_active=result.get("tracking_active", False),
            gaze_x=float(result.get("gaze_x", 0.0)),
            gaze_y=float(result.get("gaze_y", 0.0)),
            confidence=float(result.get("confidence", 0.0)),
            pitch=float(result.get("pitch", 0.0)),
            yaw=float(result.get("yaw", 0.0)),
            roll=float(result.get("roll", 0.0)),
            timestamp=time.time()
        )
        
        # Transmissão assíncrona (Broadcast)
        await manager.broadcast(session_id, packet.dict())
        
    except Exception as e:
        print(f"Erro na transmissão da sessão {session_id}: {e}")
