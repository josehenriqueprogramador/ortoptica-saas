import time
import math
from typing import Dict, Any, Optional
import numpy as np

class FaceMeshTracker:
    """
    Subsistema de Visão Computacional baseado em extração de malha facial.
    Isola e rastreia os pontos anatômicos críticos dos olhos e pupilas.
    """
    def __init__(self):
        self.use_fallback = False
        self._initialize_tracker()

    def _initialize_tracker(self):
        try:
            import mediapipe as mp
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            print("👁️ [Vision Engine] MediaPipe Face Mesh carregado com refinamento de íris ativo.")
        except Exception as e:
            print(f"⚠️ MediaPipe real não inicializado (Ambiente local ou CI/CD). Ativando fallback matemático: {e}")
            self.use_fallback = True

    def extract_landmarks(self, frame: np.ndarray) -> Dict[str, Any]:
        if self.use_fallback or frame is None:
            return self._generate_mock_landmarks()

        try:
            import cv2
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)

            if not results.multi_face_landmarks:
                return {"detected": False, "landmarks": {}, "reason": "NO_FACE_IN_FRAME"}

            face_landmarks = results.multi_face_landmarks[0].landmark
            
            extracted = {
                "left_pupil": [face_landmarks[468].x, face_landmarks[468].y, face_landmarks[468].z],
                "right_pupil": [face_landmarks[473].x, face_landmarks[473].y, face_landmarks[473].z],
                "left_inner_corner": [face_landmarks[133].x, face_landmarks[133].y, face_landmarks[133].z],
                "left_outer_corner": [face_landmarks[33].x, face_landmarks[33].y, face_landmarks[33].z],
                "right_inner_corner": [face_landmarks[362].x, face_landmarks[362].y, face_landmarks[362].z],
                "right_outer_corner": [face_landmarks[263].x, face_landmarks[263].y, face_landmarks[263].z]
            }

            return {
                "detected": True,
                "landmarks": extracted,
                "source": "MEDIAPIPE_NATIVE"
            }
        except Exception as e:
            print(f"🚨 Erro em tempo de execução no tracker. Fallback acionado: {e}")
            return self._generate_mock_landmarks()

    def _generate_mock_landmarks(self) -> Dict[str, Any]:
        t = time.time()
        mock_x = 0.5 + 0.08 * math.sin(t * 1.5)
        mock_y = 0.5 + 0.05 * math.cos(t * 2.2)

        return {
            "detected": True,
            "landmarks": {
                "left_pupil": [mock_x - 0.02, mock_y, -0.05],
                "right_pupil": [mock_x + 0.02, mock_y, -0.05],
                "left_inner_corner": [0.45, 0.5, 0.0],
                "left_outer_corner": [0.40, 0.5, 0.0],
                "right_inner_corner": [0.55, 0.5, 0.0],
                "right_outer_corner": [0.60, 0.5, 0.0]
            },
            "source": "SIMULATED_MATHEMATICAL_MOCK"
        }
