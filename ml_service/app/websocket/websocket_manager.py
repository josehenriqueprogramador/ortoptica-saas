from fastapi import WebSocket
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        self.active_connections = defaultdict(list)

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)

    async def broadcast(self, session_id: str, data: dict):
        if session_id not in self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_json(data)
            except Exception:
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(session_id, connection)

manager = ConnectionManager()
