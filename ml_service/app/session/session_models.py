from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

# --- Pydantic (Para comunicação via WebSocket/API) ---
class TelemetryPacket(BaseModel):
    session_id: str
    tracking_active: bool
    gaze_x: float
    gaze_y: float
    confidence: float
    pitch: float
    yaw: float
    roll: float
    timestamp: float

# --- SQLAlchemy (ORM para Persistência) ---
class ExaminationSession(Base):
    __tablename__ = "examination_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    patient_id: Mapped[int] = mapped_column(Integer, index=True)
    orthoptist_id: Mapped[int] = mapped_column(Integer, index=True)
    status: Mapped[str] = mapped_column(String(30), default="CREATED")
    
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    telemetry_points: Mapped[List["TelemetryMetric"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    clinical_results: Mapped[List["ClinicalResult"]] = relationship(back_populates="session", cascade="all, delete-orphan")

class TelemetryMetric(Base):
    __tablename__ = "telemetry_metrics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("examination_sessions.id"), index=True)
    
    tracking_active: Mapped[bool] = mapped_column(default=False)
    gaze_x: Mapped[float] = mapped_column(Float)
    gaze_y: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    pitch: Mapped[float] = mapped_column(Float)
    yaw: Mapped[float] = mapped_column(Float)
    roll: Mapped[float] = mapped_column(Float)
    acquisition_timestamp: Mapped[float] = mapped_column(Float)
    
    session: Mapped["ExaminationSession"] = relationship(back_populates="telemetry_points")

    __table_args__ = (
        Index("idx_telemetry_session_time", "session_id", "acquisition_timestamp"),
    )

class ClinicalResult(Base):
    __tablename__ = "clinical_results"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("examination_sessions.id"), index=True)
    
    bcea: Mapped[float] = mapped_column(Float)
    sigma_x: Mapped[float] = mapped_column(Float)
    sigma_y: Mapped[float] = mapped_column(Float)
    correlation: Mapped[float] = mapped_column(Float)
    points_count: Mapped[int] = mapped_column(Integer)
    
    horizontal_prism: Mapped[float] = mapped_column(Float)
    vertical_prism: Mapped[float] = mapped_column(Float)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    session: Mapped["ExaminationSession"] = relationship(back_populates="clinical_results")
