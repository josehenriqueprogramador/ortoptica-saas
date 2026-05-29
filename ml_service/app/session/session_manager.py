from typing import Dict, Optional
from app.session.session_runtime import SessionRuntime

class SessionManager:
    """
    Gerenciador central das sessões clínicas ativas.
    Estrutura preparada para futura migração para Redis.
    """

    def __init__(self):
        self._sessions: Dict[str, SessionRuntime] = {}

    def create_session(
        self,
        session_id: str,
        patient_id: int,
        orthoptist_id: int
    ) -> SessionRuntime:

        runtime = SessionRuntime(
            session_id=session_id,
            patient_id=patient_id,
            orthoptist_id=orthoptist_id
        )

        self._sessions[session_id] = runtime
        return runtime

    def get_session(
        self,
        session_id: str
    ) -> Optional[SessionRuntime]:

        return self._sessions.get(session_id)

    def remove_session(
        self,
        session_id: str
    ):

        if session_id in self._sessions:
            del self._sessions[session_id]

    def exists(
        self,
        session_id: str
    ) -> bool:

        return session_id in self._sessions

    def active_sessions_count(self) -> int:
        return len(self._sessions)

# Singleton global do runtime clínico
session_manager = SessionManager()
