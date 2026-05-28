import asyncio
import time
from typing import List, Dict, Any
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from ml_service.database import GazeFrameTable, engine

class OcularTelemetryBuffer:
    def __init__(self, session_id: int, batch_size: int = 30):
        self.session_id = session_id
        self.batch_size = batch_size
        self.buffer: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def append_frame(self, confidence: float, head_pose: Dict[str, float], 
                           gaze_left: Dict[str, float], gaze_right: Dict[str, float], 
                           interocular_diff: float, blink_detected: bool, 
                           acq_timestamp: float) -> None:
        processing_timestamp = time.time()
        latency_ms = (processing_timestamp - acq_timestamp) * 1000.0

        frame_data = {
            "session_id": self.session_id,
            "acquisition_timestamp": acq_timestamp,
            "processing_timestamp": processing_timestamp,
            "confidence": confidence,
            "head_pitch": head_pose.get("pitch", 0.0),
            "head_yaw": head_pose.get("yaw", 0.0),
            "left_horizontal": gaze_left.get("horizontal", 0.0),
            "left_vertical": gaze_left.get("vertical", 0.0),
            "right_horizontal": gaze_right.get("horizontal", 0.0),
            "right_vertical": gaze_right.get("vertical", 0.0),
            "interocular_diff": interocular_diff,
            "blink_detected": blink_detected,
            "latency_ms": latency_ms
        }

        async with self._lock:
            self.buffer.append(frame_data)
            
        if len(self.buffer) >= self.batch_size:
            await self.flush()

    async def flush(self) -> None:
        async with self._lock:
            if not self.buffer:
                return
            batch_to_insert = list(self.buffer)
            self.buffer.clear()

        try:
            async with AsyncSession(engine) as session:
                async with session.begin():
                    await session.execute(
                        insert(GazeFrameTable),
                        batch_to_insert
                    )
                await session.commit()
        except Exception as e:
            print(f"⚠️ [CRITICAL] Falha no bulk insert da sessão {self.session_id}: {e}")
