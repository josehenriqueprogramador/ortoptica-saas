from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.websocket.websocket_manager import manager
from app.api.consolidation_endpoint import router as clinical_router

app = FastAPI(title="Precision Vision", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clinical_router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "online", "service": "Precision Vision ML"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.websocket("/ws/live/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
