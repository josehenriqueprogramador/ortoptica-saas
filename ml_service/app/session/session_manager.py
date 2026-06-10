import json
from typing import Optional, Dict
import redis.asyncio as redis
from app.core.config import settings

class SessionManager:
    """
    Gerenciador central de sessões clínicas conectado ao Redis para suportar escalabilidade (Múltiplos workers FastAPI).
    """
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.prefix = "clinical_session:"

    async def create_session(self, session_id: str, patient_id: int, orthoptist_id: int) -> Dict:
        session_data = {
            "session_id": session_id,
            "patient_id": patient_id,
            "orthoptist_id": orthoptist_id,
            "status": "CREATED"
        }
        
        await self.redis.set(
            f"{self.prefix}{session_id}",
            json.dumps(session_data),
            ex=settings.SESSION_TIMEOUT_SECONDS
        )
        return session_data

    async def get_session(self, session_id: str) -> Optional[Dict]:
        data = await self.redis.get(f"{self.prefix}{session_id}")
        if data:
            return json.loads(data)
        return None

    async def remove_session(self, session_id: str) -> None:
        await self.redis.delete(f"{self.prefix}{session_id}")

    async def exists(self, session_id: str) -> bool:
        return await self.redis.exists(f"{self.prefix}{session_id}") > 0

session_manager = SessionManager()
