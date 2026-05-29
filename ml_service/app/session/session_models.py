import datetime
from typing import List
from sqlalchemy import String, ForeignKey, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class ClinicalSession(Base):
    """
    Representa o ciclo de vida persistente de um teste ortóptico.
    Mapeia os metadados regulatórios e o escore consolidado final.
    """
    __tablename__ = "clinical_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="CREATED")  # CREATED, ACTIVE, CONSOLIDATED, ABORTED
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    bcea_score: Mapped[float] = mapped_column(Float, nullable=True)  # Calculado estatisticamente pós-consolidação

    # Relacionamento 1:N com as séries temporais de rastreamento visual
    telemetry_points: Mapped[List["GazeTelemetryPoint"]] = relationship(
        "GazeTelemetryPoint", back_populates="session", cascade="all, delete-orphan"
    )

class GazeTelemetryPoint(Base):
    """
    Série temporal contínua capturada via WebSocket.
    Alimenta o pipeline estatístico de estabilidade ocular (BCEA).
    """
    __tablename__ = "gaze_telemetry_series"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("clinical_sessions.id", ondelete="CASCADE"), index=True)
    timestamp: Mapped[float] = mapped_column(Float, index=True)
    gaze_x: Mapped[float] = mapped_column(Float)
    gaze_y: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    current_target: Mapped[str] = mapped_column(String(50))

    session: Mapped["ClinicalSession"] = relationship("ClinicalSession", back_populates="telemetry_points")
