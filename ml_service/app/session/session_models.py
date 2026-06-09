from pydantic import BaseModel
from typing import Optional

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
