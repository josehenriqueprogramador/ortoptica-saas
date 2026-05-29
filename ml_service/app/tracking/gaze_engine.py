import numpy as np
from typing import Dict, Any
from app.tracking.facemesh_tracker import FaceMeshTracker
from app.tracking.pose_estimator import PoseEstimator
from app.tracking.gaze_vector import GazeVectorCalculator
from app.tracking.temporal_filter import TemporalFilter

class GazeEngine:
    """
    Orquestrador mestre (Fachada) do pipeline biométrico.
    Gerencia o fluxo linear de dados: Frame -> Landmarks -> Pose -> Gaze -> Filtro.
    """

    def __init__(self):
        # Instanciação acoplada dos nós de processamento da esteira
        self.tracker = FaceMeshTracker()
        self.pose_estimator = PoseEstimator()
        self.gaze_calculator = GazeVectorCalculator()
        self.filter = TemporalFilter()
        print("🚀 [GazeEngine] Pipeline de processamento unificado inicializado com sucesso.")

    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Executa a transformação síncrona do frame de imagem em coordenadas de foveação.
        Garante tolerância a falhas caso o rosto saia do campo de visão da câmera.
        """
        # 1. Extração de Landmarks Anatômicos
        tracking_result = self.tracker.extract_landmarks(frame)
        
        if not tracking_result["detected"]:
            return {
                "tracking_active": False,
                "gaze_x": 0.0,
                "gaze_y": 0.0,
                "confidence": 0.0,
                "head_pose": {"pitch": 0.0, "yaw": 0.0, "roll": 0.0},
                "status": tracking_result.get("reason", "TRACKING_FAILED")
            }

        landmarks = tracking_result["landmarks"]
        
        # Recupera dimensões do frame para mapeamento espacial proporcional se necessário
        height, width = frame.shape[:2] if frame is not None else (480, 640)

        # 2. Cálculo da Pose Craniométrica (6 DoF)
        pose_result = self.pose_estimator.estimate_head_pose(landmarks, width, height)

        # 3. Cálculo do Vetor de Olhar Bruto (com compensação de movimento de cabeça)
        gaze_result = self.gaze_calculator.calculate_gaze_coordinate(landmarks, pose_result["angles"])

        if not gaze_result["gaze_valid"]:
            return {
                "tracking_active": True,
                "gaze_x": 0.0,
                "gaze_y": 0.0,
                "confidence": 0.0,
                "head_pose": pose_result["angles"],
                "status": gaze_result["status"]
            }

        # 4. Suavização Temporal Passa-Baixa (Remoção de Jitter)
        filtered_x, filtered_y = self.filter.filter(gaze_result["gaze_x"], gaze_result["gaze_y"])

        # Encapsulamento estruturado do payload final de telemetria
        return {
            "tracking_active": True,
            "gaze_x": filtered_x,
            "gaze_y": filtered_y,
            "confidence": gaze_result["confidence"],
            "head_pose": pose_result["angles"],
            "status": "PROCESSED_SUCCESSFULLY"
        }

    def reset_engine_state(self) -> None:
        """Reinicia os buffers históricos para preparar o motor para um novo paciente."""
        self.filter.reset()
        print("🧹 [GazeEngine] Histórico de filtros temporais redefinido.")
