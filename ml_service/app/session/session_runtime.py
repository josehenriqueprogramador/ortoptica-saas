import time
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.session.session_models import GazeTelemetryPoint

class SessionRuntime:
    """
    Gerenciador volátil de estado de exame em memória RAM.
    Otimiza o pipeline coletando pontos a 30 FPS para persistência em lote posterior.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_target = "CENTER_FIXATION"
        
        # Buffer de alta velocidade para evitar acessos concorrentes ao disco
        self._telemetry_buffer: List[Dict[str, Any]] = []
        self.started_at = time.time()

    def update_target(self, target_label: str):
        """Atualiza dinamicamente o alvo clínico ativo no loop médico."""
        self.current_target = target_label

    def register_frame(self, gaze_x: float, gaze_y: float, confidence: float, latency: float):
        """
        Adiciona os metadados biométricos extraídos ao buffer em memória volátil.
        """
        self._telemetry_buffer.append({
            "timestamp": time.time(),
            "gaze_x": gaze_x,
            "gaze_y": gaze_y,
            "confidence": confidence,
            "current_target": self.current_target
        })

    def get_buffered_points(self) -> List[Dict[str, Any]]:
        """Retorna a série temporal acumulada para processamento analítico."""
        return self._telemetry_buffer

    async def flush_to_database(self, db: AsyncSession):
        """
        Descarrega todo o buffer acumulado em memória em um único lote estruturado (Bulk Insert).
        Evita overhead de rede e garante integridade referencial nas séries temporais.
        """
        if not self._telemetry_buffer:
            return

        db_points = [
            GazeTelemetryPoint(
                session_id=self.session_id,
                timestamp=p["timestamp"],
                gaze_x=p["gaze_x"],
                gaze_y=p["gaze_y"],
                confidence=p["confidence"],
                current_target=p["current_target"]
            )
            for p in self._telemetry_buffer
        ]

        # Injeção em bloco altamente eficiente
        db.add_all(db_points)
        await db.flush()
        
        # Limpa o buffer de memória após garantia de persistência
        self._telemetry_buffer.clear()
