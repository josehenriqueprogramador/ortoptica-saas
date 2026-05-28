import os
import math
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, BigInteger, Float, String, Boolean, DateTime, ForeignKey, Integer, Double, Index

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://root:root@localhost:3306/ortoptica_saas")

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=20, max_overflow=10)
Base = declarative_base()

class ClinicalSessionTable(Base):
    __tablename__ = 'clinical_sessions'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patient_id = Column(BigInteger, nullable=False)
    operator_id = Column(BigInteger, nullable=True)
    engine_version = Column(String(20), default="11.0.0")
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    average_confidence = Column(Float, nullable=True)
    discarded_frames = Column(Integer, default=0)
    morph_scale = Column(Float, nullable=True)
    eyeball_radius_mm = Column(Float, nullable=True)
    calibration_fitted = Column(Boolean, default=False)
    exam_duration_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class GazeFrameTable(Base):
    __tablename__ = 'gaze_frames'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey('clinical_sessions.id'), nullable=False)
    acquisition_timestamp = Column(Double, nullable=False)
    processing_timestamp = Column(Double, nullable=False)
    confidence = Column(Float, nullable=False)
    head_pitch = Column(Float, nullable=False)
    head_yaw = Column(Float, nullable=False)
    left_horizontal = Column(Float, nullable=False)
    left_vertical = Column(Float, nullable=False)
    right_horizontal = Column(Float, nullable=False)
    right_vertical = Column(Float, nullable=False)
    interocular_diff = Column(Float, nullable=False)
    blink_detected = Column(Boolean, default=False)
    latency_ms = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index('idx_session_frames', 'session_id'),)

class NineGazePositionsTable(Base):
    __tablename__ = 'nine_gaze_positions'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey('clinical_sessions.id'), nullable=False)
    gaze_position = Column(String(30), nullable=False)
    horizontal_deviation_deg = Column(Float, nullable=False)
    vertical_deviation_deg = Column(Float, nullable=False)
    prism_diopters = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    suspected_condition = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
