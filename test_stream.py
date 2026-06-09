import asyncio
import time
from ml_service.app.websocket.websocket_manager import manager
from ml_service.app.session.session_runtime import process_and_broadcast

async def simulate_stream():
    print("🚀 Iniciando simulação de streaming de telemetria...")
    
    # Simulando um session_id que o seu front-end usaria
    session_id = "test-session-001"
    
    # Simulando 5 frames de dados vindo do GazeEngine
    for i in range(5):
        mock_data = {
            "tracking_active": True,
            "gaze_x": 0.1 * i,
            "gaze_y": -0.05 * i,
            "confidence": 0.95,
            "pitch": 0.0,
            "yaw": 0.0,
            "roll": 0.0
        }
        
        print(f"📦 Enviando frame {i+1}...")
        await process_and_broadcast(session_id, mock_data)
        await asyncio.sleep(1) # Intervalo de 1 segundo entre frames
        
    print("✅ Simulação concluída.")

if __name__ == "__main__":
    # Nota: Este teste assume que o manager está instanciado.
    # Em um ambiente real, o FastAPI cuidaria disso.
    try:
        asyncio.run(simulate_stream())
    except Exception as e:
        print(f"⚠️ Erro na simulação: {e}")
